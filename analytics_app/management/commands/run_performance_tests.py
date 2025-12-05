# analytics_app/management/commands/run_performance_tests.py
import time
import statistics
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
import json

class Command(BaseCommand):
    help = 'Run performance tests on all API endpoints'
    
    def handle(self, *args, **options):
        client = Client()
        results = {}
        
        test_cases = [
            {
                'name': 'API #1 - Blog Views by Country',
                'url': '/analytics/blog-views/',
                'params': {'object_type': 'country', 'range': 'month'}
            },
            {
                'name': 'API #1 - Blog Views by User',
                'url': '/analytics/blog-views/',
                'params': {'object_type': 'user', 'range': 'month'}
            },
            {
                'name': 'API #2 - Top Users',
                'url': '/analytics/top/',
                'params': {'top': 'user'}
            },
            {
                'name': 'API #2 - Top Countries',
                'url': '/analytics/top/',
                'params': {'top': 'country'}
            },
            {
                'name': 'API #2 - Top Blogs',
                'url': '/analytics/top/',
                'params': {'top': 'blog'}
            },
            {
                'name': 'API #3 - Monthly Performance',
                'url': '/analytics/performance/',
                'params': {'compare': 'month'}
            },
            {
                'name': 'API #3 - Weekly Performance',
                'url': '/analytics/performance/',
                'params': {'compare': 'week'}
            },
        ]
        
        for test_case in test_cases:
            self.stdout.write(f"\nTesting: {test_case['name']}")
            
            response_times = []
            for i in range(10):  # Run 10 iterations
                start_time = time.perf_counter()
                response = client.get(test_case['url'], test_case['params'])
                end_time = time.perf_counter()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                
                if i == 0:  # First response
                    status = "✓" if response.status_code == 200 else "✗"
                    self.stdout.write(f"  {status} Status: {response.status_code}")
            
            # Calculate statistics
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0
            
            results[test_case['name']] = {
                'avg_response_time_ms': round(avg_time, 2),
                'min_response_time_ms': round(min_time, 2),
                'max_response_time_ms': round(max_time, 2),
                'std_dev_ms': round(std_dev, 2),
                'iterations': len(response_times)
            }
            
            self.stdout.write(f"  Average: {avg_time:.2f}ms")
            self.stdout.write(f"  Range: {min_time:.2f}ms - {max_time:.2f}ms")
        
        # Print summary
        self.stdout.write("\n" + "="*50)
        self.stdout.write("PERFORMANCE TEST SUMMARY")
        self.stdout.write("="*50)
        
        for test_name, stats in results.items():
            self.stdout.write(f"\n{test_name}:")
            for key, value in stats.items():
                self.stdout.write(f"  {key.replace('_', ' ').title()}: {value}")