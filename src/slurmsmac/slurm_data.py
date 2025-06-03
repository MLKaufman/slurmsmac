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

    def get_active_jobs(self) -> pd.DataFrame:
        """Get currently active and pending jobs."""
        cmd = ['squeue', '-u', self.username, '--format=%i|%j|%t|%M|%N|%C|%m|%R']
        output = subprocess.check_output(cmd).decode()
        
        # Parse the output
        lines = output.strip().split('\n')[1:]  # Skip header
        data = []
        for line in lines:
            job_id, name, state, time, nodes, cpus, mem, reason = line.split('|')
            data.append({
                'job_id': job_id,
                'name': name,
                'state': state,
                'time': time,
                'nodes': nodes,
                'cpus': cpus,
                'memory': mem,
                'reason': reason
            })
        
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
        output = subprocess.check_output(cmd).decode()
        
        # Parse the output
        lines = output.strip().split('\n')[1:]  # Skip header
        data = []
        for line in lines:
            if not line.strip():
                continue
            fields = line.split()
            if len(fields) >= 10:
                data.append({
                    'job_id': fields[0],
                    'name': fields[1],
                    'state': fields[2],
                    'start': fields[3],
                    'end': fields[4],
                    'elapsed': fields[5],
                    'max_rss': fields[6],
                    'max_vmsize': fields[7],
                    'ncpus': fields[8],
                    'nodes': fields[9]
                })
        
        return pd.DataFrame(data)

    def get_job_stats(self) -> Dict:
        """Get overall job statistics."""
        history_df = self.get_job_history()
        active_df = self.get_active_jobs()
        
        stats = {
            'total_jobs': len(history_df) + len(active_df),
            'active_jobs': len(active_df),
            'completed_jobs': len(history_df[history_df['state'] == 'COMPLETED']),
            'failed_jobs': len(history_df[history_df['state'] == 'FAILED']),
            'cancelled_jobs': len(history_df[history_df['state'] == 'CANCELLED']),
            'avg_cpu_usage': history_df['ncpus'].astype(float).mean() if not history_df.empty else 0,
            'avg_memory_usage': history_df['max_rss'].str.replace('K', '').astype(float).mean() if not history_df.empty else 0
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