"""
Progress Manager for DualMind
Provides detailed progress tracking for processing operations
"""

import time
from datetime import datetime

class ProgressManager:
    def __init__(self):
        self.progress_data = {}
    
    def start_progress(self, process_id, total_steps=100):
        """Start tracking progress for a process"""
        self.progress_data[process_id] = {
            'start_time': time.time(),
            'current_step': 0,
            'total_steps': total_steps,
            'status': 'starting',
            'message': 'Initializing...',
            'detailed_steps': [],
            'current_progress': 0
        }
    
    def update_progress(self, process_id, step, message, progress_percent=None):
        """Update progress for a specific step"""
        if process_id not in self.progress_data:
            return
        
        data = self.progress_data[process_id]
        data['current_step'] = step
        data['message'] = message
        data['status'] = 'processing'
        
        if progress_percent is not None:
            data['current_progress'] = min(100, max(0, progress_percent))
        else:
            # Auto-calculate based on steps
            data['current_progress'] = min(100, (step / data['total_steps']) * 100)
        
        # Add to detailed steps log
        data['detailed_steps'].append({
            'step': step,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'elapsed_time': round(time.time() - data['start_time'], 1)
        })
        
        # Keep only last 10 detailed steps
        if len(data['detailed_steps']) > 10:
            data['detailed_steps'] = data['detailed_steps'][-10:]
    
    def complete_progress(self, process_id, final_message="Processing completed successfully"):
        """Mark progress as completed"""
        if process_id not in self.progress_data:
            return
        
        data = self.progress_data[process_id]
        data['current_progress'] = 100
        data['status'] = 'completed'
        data['message'] = final_message
        data['end_time'] = time.time()
        data['total_time'] = round(data['end_time'] - data['start_time'], 1)
    
    def set_error(self, process_id, error_message):
        """Mark progress as failed with error"""
        if process_id not in self.progress_data:
            return
        
        data = self.progress_data[process_id]
        data['status'] = 'error'
        data['message'] = f"Error: {error_message}"
        data['end_time'] = time.time()
        data['total_time'] = round(data['end_time'] - data['start_time'], 1)
    
    def get_progress(self, process_id):
        """Get current progress data"""
        return self.progress_data.get(process_id, {
            'current_progress': 0,
            'status': 'not_found',
            'message': 'Process not found',
            'detailed_steps': []
        })
    
    def cleanup_progress(self, process_id, delay_seconds=300):
        """Clean up progress data after completion (5 minutes default)"""
        if process_id in self.progress_data:
            data = self.progress_data[process_id]
            if data.get('status') in ['completed', 'error']:
                # In a real app, you'd use a background task
                # For now, we'll just mark for cleanup
                data['cleanup_after'] = time.time() + delay_seconds

# Create global progress manager instance
progress_manager = ProgressManager()