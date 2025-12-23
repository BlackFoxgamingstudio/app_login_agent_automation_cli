"""
Workflow State Management
Handles saving, loading, and resuming workflow state for checkpoint/resume functionality.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WorkflowState:
    """Manages workflow state for checkpoint and resume functionality."""
    
    def __init__(self, workflow_id: Optional[str] = None, state_dir: str = "workflows"):
        """
        Initialize workflow state manager.
        
        Args:
            workflow_id: Optional workflow ID (generates new if not provided)
            state_dir: Directory to store workflow state files
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path = self.state_dir / self.workflow_id / "checkpoint.json"
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.state: Dict[str, Any] = {
            'workflow_id': self.workflow_id,
            'grant_name': None,
            'steps_completed': [],
            'current_step': None,
            'state': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'checkpoint_path': str(self.checkpoint_path)
        }
    
    def set_grant_name(self, grant_name: str):
        """Set the grant name for this workflow."""
        self.state['grant_name'] = grant_name
        self.state['updated_at'] = datetime.now().isoformat()
    
    def add_completed_step(self, step_name: str):
        """Mark a step as completed."""
        if step_name not in self.state['steps_completed']:
            self.state['steps_completed'].append(step_name)
        self.state['current_step'] = step_name
        self.state['updated_at'] = datetime.now().isoformat()
    
    def set_current_step(self, step_name: str):
        """Set the current step."""
        self.state['current_step'] = step_name
        self.state['updated_at'] = datetime.now().isoformat()
    
    def save_state_data(self, key: str, data: Any):
        """Save data to workflow state."""
        if 'state' not in self.state:
            self.state['state'] = {}
        self.state['state'][key] = data
        self.state['updated_at'] = datetime.now().isoformat()
    
    def get_state_data(self, key: str, default: Any = None) -> Any:
        """Get data from workflow state."""
        return self.state.get('state', {}).get(key, default)
    
    def save_checkpoint(self) -> str:
        """
        Save current state to checkpoint file.
        
        Returns:
            Path to checkpoint file
        """
        try:
            with open(self.checkpoint_path, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            logger.info(f"Checkpoint saved to {self.checkpoint_path}")
            return str(self.checkpoint_path)
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
            raise
    
    def load_checkpoint(self) -> bool:
        """
        Load state from checkpoint file.
        
        Returns:
            True if checkpoint loaded successfully, False otherwise
        """
        if not self.checkpoint_path.exists():
            return False
        
        try:
            with open(self.checkpoint_path, 'r') as f:
                self.state = json.load(f)
            logger.info(f"Checkpoint loaded from {self.checkpoint_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return False
    
    def is_step_completed(self, step_name: str) -> bool:
        """Check if a step has been completed."""
        return step_name in self.state.get('steps_completed', [])
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get workflow progress information.
        
        Returns:
            Dictionary with progress details
        """
        steps_completed = len(self.state.get('steps_completed', []))
        total_steps = 16  # Approximate total steps
        
        return {
            'workflow_id': self.workflow_id,
            'grant_name': self.state.get('grant_name'),
            'steps_completed': steps_completed,
            'total_steps': total_steps,
            'progress_percentage': int((steps_completed / total_steps) * 100) if total_steps > 0 else 0,
            'current_step': self.state.get('current_step'),
            'completed_steps': self.state.get('steps_completed', []),
            'created_at': self.state.get('created_at'),
            'updated_at': self.state.get('updated_at')
        }
    
    def reset(self):
        """Reset workflow state."""
        self.state = {
            'workflow_id': self.workflow_id,
            'grant_name': None,
            'steps_completed': [],
            'current_step': None,
            'state': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'checkpoint_path': str(self.checkpoint_path)
        }
    
    @staticmethod
    def load_from_checkpoint(checkpoint_path: str) -> Optional['WorkflowState']:
        """
        Load workflow state from a checkpoint file.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            WorkflowState instance or None if loading failed
        """
        try:
            with open(checkpoint_path, 'r') as f:
                state_data = json.load(f)
            
            workflow_id = state_data.get('workflow_id')
            if not workflow_id:
                return None
            
            workflow_state = WorkflowState(workflow_id=workflow_id)
            workflow_state.state = state_data
            return workflow_state
        except Exception as e:
            logger.error(f"Error loading checkpoint from {checkpoint_path}: {e}")
            return None
    
    @staticmethod
    def list_workflows(state_dir: str = "workflows") -> List[Dict[str, Any]]:
        """
        List all available workflows.
        
        Args:
            state_dir: Directory containing workflow states
            
        Returns:
            List of workflow information dictionaries
        """
        workflows = []
        state_path = Path(state_dir)
        
        if not state_path.exists():
            return workflows
        
        for workflow_dir in state_path.iterdir():
            if not workflow_dir.is_dir():
                continue
            
            checkpoint_path = workflow_dir / "checkpoint.json"
            if not checkpoint_path.exists():
                continue
            
            try:
                with open(checkpoint_path, 'r') as f:
                    state_data = json.load(f)
                
                workflows.append({
                    'workflow_id': state_data.get('workflow_id'),
                    'grant_name': state_data.get('grant_name'),
                    'steps_completed': len(state_data.get('steps_completed', [])),
                    'current_step': state_data.get('current_step'),
                    'created_at': state_data.get('created_at'),
                    'updated_at': state_data.get('updated_at'),
                    'checkpoint_path': str(checkpoint_path)
                })
            except Exception as e:
                logger.warning(f"Error reading workflow {workflow_dir}: {e}")
                continue
        
        return workflows

