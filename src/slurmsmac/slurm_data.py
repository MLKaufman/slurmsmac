# -*- coding: utf-8 -*-
import subprocess
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import random
import os

class BaseSlurmDataCollector:
    """Base class for Slurm data collection."""
    def get_active_jobs(self) -> pd.DataFrame:
        """Get currently active and pending jobs."""
        raise NotImplementedError

    def get_job_history(self, days: int = 7) -> pd.DataFrame:
        """Get job history for the specified number of days."""
        raise NotImplementedError

    def get_job_stats(self) -> Dict:
        """Get overall job statistics."""
        raise NotImplementedError

class MockSlurmDataCollector(BaseSlurmDataCollector):
    """Mock implementation for systems without Slurm."""
    def __init__(self):
        self.job_states = ['RUNNING', 'PENDING', 'COMPLETED', 'FAILED', 'CANCELLED']
        self.job_names = ['simulation', 'analysis', 'training', 'inference', 'preprocessing']
        self.nodes = ['node1', 'node2', 'node3', 'compute1', 'compute2']
        
    def _generate_mock_job(self, job_id: int, is_active: bool = True) -> Dict:
        """Generate a mock job entry."""
        state = random.choice(self.job_states) if is_active else random.choice(['COMPLETED', 'FAILED', 'CANCELLED'])
        return {
            'job_id': f'{job_id}',
            'name': random.choice(self.job_names),
            'state': state,
            'time': f'{random.randint(1, 24)}:00:00',
            'nodes': random.choice(self.nodes),
            'cpus': str(random.randint(1, 32)),
            'memory': f'{random.randint(1, 64)}G',
            'reason': 'None' if state == 'RUNNING' else 'Resources' if state == 'PENDING' else 'Completed'
        }

    def get_active_jobs(self) -> pd.DataFrame:
        """Get mock active jobs."""
        num_jobs = random.randint(0, 5)
        jobs = [self._generate_mock_job(i, True) for i in range(num_jobs)]
        return pd.DataFrame(jobs)

    def get_job_history(self, days: int = 7) -> pd.DataFrame:
        """Get mock job history."""
        num_jobs = random.randint(10, 30)
        jobs = [self._generate_mock_job(i, False) for i in range(num_jobs)]
        return pd.DataFrame(jobs)

    def get_job_stats(self) -> Dict:
        """Get mock job statistics."""
        history_df = self.get_job_history()
        active_df = self.get_active_jobs()
        
        return {
            'total_jobs': len(history_df) + len(active_df),
            'active_jobs': len(active_df),
            'completed_jobs': len(history_df[history_df['state'] == 'COMPLETED']),
            'failed_jobs': len(history_df[history_df['state'] == 'FAILED']),
            'cancelled_jobs': len(history_df[history_df['state'] == 'CANCELLED']),
            'avg_cpu_usage': random.uniform(1, 32),
            'avg_memory_usage': random.uniform(1, 64)
        }

class RealSlurmDataCollector(BaseSlurmDataCollector):
    """Real implementation for systems with Slurm."""
    def __init__(self):
        self.username = self._get_username()

    def _get_username(self) -> str:
        """Get the current username."""
        return subprocess.check_output(['whoami']).decode().strip()

    def _clean_string(self, s: str) -> str:
        """Clean a string by removing or replacing problematic characters."""
        # Remove control characters and other problematic characters
        return ''.join(char for char in s if ord(char) >= 32 or char in '\n\r\t')

    def get_active_jobs(self) -> pd.DataFrame:
        """Get currently active and pending jobs."""
        cmd = ['squeue', '-u', self.username, '--format=%i|%j|%t|%M|%N|%C|%m|%R']
        try:
            output = subprocess.check_output(cmd, encoding='latin-1', errors='replace').strip()
            output = self._clean_string(output)
        except subprocess.CalledProcessError:
            return pd.DataFrame()
        
        # Parse the output
        lines = output.split('\n')[1:]  # Skip header
        data = []
        for line in lines:
            if not line.strip():
                continue
            try:
                job_id, name, state, time, nodes, cpus, mem, reason = line.split('|')
                data.append({
                    'job_id': job_id.strip(),
                    'name': name.strip(),
                    'state': state.strip(),
                    'time': time.strip(),
                    'nodes': nodes.strip(),
                    'cpus': cpus.strip(),
                    'memory': mem.strip(),
                    'reason': reason.strip()
                })
            except ValueError:
                continue
        
        return pd.DataFrame(data)

    def get_job_history(self, days: int = 7) -> pd.DataFrame:
        """Get job history for the specified number of days."""
        start_time = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y-%m-%d')
        cmd = [
            'sacct',
            '-u', self.username,
            '-S', start_time,
            '--format=JobID,JobName,State,Start,End,Elapsed,MaxRSS,MaxVMSize,NCPUS,NodeList'
        ]
        try:
            output = subprocess.check_output(cmd, encoding='latin-1', errors='replace').strip()
            output = self._clean_string(output)
        except subprocess.CalledProcessError:
            return pd.DataFrame()
        
        # Parse the output
        lines = output.split('\n')[1:]  # Skip header
        data = []
        for line in lines:
            if not line.strip():
                continue
            try:
                fields = line.split()
                if len(fields) >= 10:
                    data.append({
                        'job_id': fields[0].strip(),
                        'name': fields[1].strip(),
                        'state': fields[2].strip(),
                        'start': fields[3].strip(),
                        'end': fields[4].strip(),
                        'elapsed': fields[5].strip(),
                        'max_rss': fields[6].strip(),
                        'max_vmsize': fields[7].strip(),
                        'ncpus': fields[8].strip(),
                        'nodes': fields[9].strip()
                    })
            except (ValueError, IndexError):
                continue
        
        return pd.DataFrame(data)

    def get_job_stats(self) -> Dict:
        """Get overall job statistics."""
        history_df = self.get_job_history()
        active_df = self.get_active_jobs()
        
        # Filter out header rows and convert values safely
        valid_ncpus = history_df[history_df['ncpus'] != '----------']['ncpus'].astype(float)
        valid_memory = history_df[history_df['max_rss'] != '----------']['max_rss'].str.replace('K', '').astype(float)
        
        stats = {
            'total_jobs': len(history_df) + len(active_df),
            'active_jobs': len(active_df),
            'completed_jobs': len(history_df[history_df['state'] == 'COMPLETED']),
            'failed_jobs': len(history_df[history_df['state'] == 'FAILED']),
            'cancelled_jobs': len(history_df[history_df['state'] == 'CANCELLED']),
            'avg_cpu_usage': valid_ncpus.mean() if not valid_ncpus.empty else 0,
            'avg_memory_usage': valid_memory.mean() if not valid_memory.empty else 0
        }
        
        return stats

def get_slurm_collector() -> BaseSlurmDataCollector:
    """Get the appropriate Slurm data collector based on system availability."""
    try:
        # Try to run a simple slurm command to check if it's available
        subprocess.run(['sinfo', '--version'], capture_output=True, check=True)
        return RealSlurmDataCollector()
    except (subprocess.SubprocessError, FileNotFoundError):
        return MockSlurmDataCollector() 