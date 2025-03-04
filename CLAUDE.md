# shop-lifter Project Guide

## System Overview

The Shop-Lifter project aims to create an autonomous robotic system that combines:
- 8 Waveshare RoArm-M3 Pro robotic arms distributed across 3 carts:
  - 1 training cart with 4 arms (2 leaders, 2 followers)
  - 2 inference/test carts with 2 arms each
- Advanced perception via RealSense cameras and IMUs
- Mobile base with ODrive-controlled brushless DC motors
- NVIDIA Jetson Orin Nano (with maxed performance) for on-device AI

The system will use active inference principles to continuously learn from demonstrations, minimize prediction errors, and adapt to real-world environments.

## Hardware Specifications

### RoArm-M3 Pro Robotic Arms
- **Configuration**: 5+1 DoF (5 arm joints + gripper)
- **Servos**: ST3235 metal shell servos (Pro version) for all joints except gripper
- **Control Board**: General Driver Board with ESP32-WROOM-32 MCU
- **Communication**: WiFi, Serial, ESP-NOW for leader-follower coordination
- **Payload**: 0.2kg at 0.5m reach
- **Working Range**: Up to 1m diameter workspace

### Mobile Cart
- **Drive System**: Two 24V brushless DC motors (rear wheels)
- **Motor Controller**: ODrive board
- **Power System**: Needs detailed specification

### Perception Hardware
- **Cameras**:
  - Intel RealSense cameras for egocentric view (1 per cart)
  - Wide-angle cameras on each front arm near wrist
- **IMUs**: 9-axis IMUs on the wrist of each front follower arm
- **Processing**: NVIDIA Jetson Orin Nano (MaxN mode) - potential upgrade to Thor series

### Additional Hardware (Future)
- Proximity sensors for obstacle avoidance
- Audio input/output

## Key Technologies & Libraries

### Core ML Frameworks
- PyTorch for neural network implementations
- Hugging Face Transformers for BERT-like components

### Computer Vision
- OpenCV for camera input processing
- SAM2 (Segment Anything Model v2) for object segmentation
- Intel RealSense SDK

### Robotics & Control
- ROS2 (Robot Operating System) for hardware communication
- ODrive Python API for motor control
- PyBullet for physics simulation and testing
- ESP-NOW for leader-follower coordination

### Active Inference & Learning
- Transformer-based bidirectional encoder (BERT-like)
- Multi-head attention mechanisms for parallel feature processing
- Chain-of-Draft approach for iterative reasoning
- Free Energy Principle implementation

## Project Scaffold

The following outlines the folder structure and pseudo-code files for the initial project scaffold:

```
shop-lifter/
├── hardware/
│   ├── RoArm-M3/                       # Cloned research repository
│   ├── arm_interface/
│   │   ├── __init__.py
│   │   ├── arm_controller.py           # Interface to RoArm-M3 JSON API
│   │   ├── leader_follower.py          # ESP-NOW leader-follower implementation
│   │   └── servo_control.py            # Direct servo control functions
│   ├── cart/
│   │   ├── __init__.py
│   │   ├── odrive_controller.py        # Control for mobile base motors
│   │   ├── navigation.py               # Navigation and path planning
│   │   └── power_management.py         # Power system management
│   └── sensors/
│       ├── __init__.py
│       ├── realsense.py                # RealSense camera interface
│       ├── imu.py                      # 9-axis IMU integration
│       └── sensor_fusion.py            # Fusion of vision and IMU data
├── perception/
│   ├── __init__.py
│   ├── sam2/
│   │   ├── __init__.py
│   │   ├── model.py                    # SAM2 model integration
│   │   ├── inference.py                # Real-time segmentation
│   │   └── utils.py                    # Utilities for SAM2
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── object_detection.py         # Object detection pipeline
│   │   ├── scene_understanding.py      # Scene graph generation
│   │   └── spatial_mapping.py          # 3D spatial mapping
│   └── multimodal/
│       ├── __init__.py
│       ├── encoder.py                  # Multi-modal fusion encoder
│       ├── embeddings.py               # Feature embedding extraction
│       └── attention.py                # Multi-head attention implementation
├── models/
│   ├── __init__.py
│   ├── transformer/
│   │   ├── __init__.py
│   │   ├── encoder.py                  # BERT-like encoder implementation
│   │   ├── attention.py                # Multi-head attention mechanism
│   │   └── positional_encoding.py      # Positional encoding for transformers
│   ├── forward_model/
│   │   ├── __init__.py
│   │   ├── state_predictor.py          # Predicts future states from current
│   │   ├── uncertainty_estimator.py    # Estimates prediction uncertainty
│   │   └── training.py                 # Training routines for forward model
│   └── active_inference/
│       ├── __init__.py
│       ├── free_energy.py              # Free energy computation
│       ├── policy_selection.py         # Action selection to minimize free energy
│       └── belief_updating.py          # Belief update based on sensory evidence
├── training/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dataset.py                  # Dataset creation from demonstrations
│   │   ├── augmentation.py             # Data augmentation techniques
│   │   └── preprocessing.py            # Preprocessing pipelines
│   ├── imitation/
│   │   ├── __init__.py
│   │   ├── demonstration.py            # Recording human demonstrations
│   │   ├── behavior_cloning.py         # Direct imitation learning
│   │   └── inverse_dynamics.py         # Learning action from state transitions
│   └── co_training/
│       ├── __init__.py
│       ├── static_pretraining.py       # Pretraining on static datasets
│       ├── online_adaptation.py        # Online learning from demonstrations
│       └── action_chunking.py          # Action sequence optimization
├── inference/
│   ├── __init__.py
│   ├── planner/
│   │   ├── __init__.py
│   │   ├── task_decomposition.py       # Breaking tasks into subtasks
│   │   ├── chain_of_draft.py           # Multi-draft reasoning for planning
│   │   └── motion_planning.py          # Arm trajectory planning
│   └── execution/
│       ├── __init__.py
│       ├── controller.py               # Real-time control loop
│       ├── monitoring.py               # Execution monitoring
│       └── error_recovery.py           # Error detection and recovery
├── utils/
│   ├── __init__.py
│   ├── config.py                      # Configuration management
│   ├── logging.py                     # Logging utilities
│   ├── visualization.py               # Visualization tools
│   └── profiling.py                   # Performance profiling tools
├── tests/
│   ├── unit/                          # Unit tests for each module
│   ├── integration/                   # Integration tests
│   └── hardware/                      # Hardware-specific tests
└── scripts/
    ├── setup/
    │   ├── install_dependencies.sh    # Installation script
    │   ├── configure_hardware.sh      # Hardware configuration
    │   └── setup_environment.sh       # Environment setup
    ├── demos/
    │   ├── arm_test.py                # Basic arm movement test
    │   ├── leader_follower_demo.py    # Leader-follower demonstration
    │   └── perception_test.py         # Vision system test
    └── evaluation/
        ├── benchmark_perception.py    # Benchmark perception system
        ├── benchmark_control.py       # Benchmark control system
        └── benchmark_inference.py     # Benchmark inference pipeline
```

## Pseudo-Code Components

### Hardware Interface

#### `arm_controller.py`
```python
"""
Interface to the RoArm-M3 Pro arms using JSON commands.

Research references:
- RoArm-M3 JSON Command System: /hardware/RoArm-M3/research/software/JSON_Command_System.md
- Python API: /hardware/RoArm-M3/research/software/Python_API.md
"""

class ArmController:
    """Controls a single RoArm-M3 Pro arm via HTTP or Serial."""
    
    def __init__(self, connection_type='http', address='192.168.4.1', port=None):
        """
        Initialize connection to arm.
        
        Args:
            connection_type: Either 'http' or 'serial'
            address: IP address for HTTP or device path for serial
            port: Serial port (for serial connection only)
        """
        # Initialize connection based on type
        pass
        
    def send_command(self, command):
        """
        Send a JSON command to the arm.
        
        Args:
            command: Dictionary containing the JSON command
            
        Returns:
            Dictionary containing the response
        """
        # Format command as JSON and send via appropriate channel
        pass
        
    def move_joint(self, joint_id, angle, speed=50):
        """
        Move a specific joint to the given angle.
        
        Args:
            joint_id: Joint ID (0-5)
            angle: Target angle in radians
            speed: Movement speed (0-100)
        """
        # Construct and send joint control command
        pass
        
    def move_to_position(self, x, y, z, roll=0, pitch=0, yaw=0, speed=50):
        """
        Move arm end effector to a specific position using inverse kinematics.
        
        Args:
            x, y, z: Target position coordinates
            roll, pitch, yaw: Target orientation
            speed: Movement speed (0-100)
        """
        # Construct and send coordinate control command
        pass
    
    def get_current_position(self):
        """Get current end effector position and orientation."""
        # Query current position
        pass
    
    def get_joint_angles(self):
        """Get current joint angles."""
        # Query current joint angles
        pass
```

#### `leader_follower.py`
```python
"""
Implementation of leader-follower functionality for RoArm-M3 Pro.

Research references:
- Leader-Follower Mode: /hardware/RoArm-M3/leader_follower_mode/README.md
- ESP-NOW Protocol: /hardware/RoArm-M3/research/hardware/communication/ESP_NOW_Protocol.md
"""

class LeaderController:
    """Controls a leader arm that broadcasts to followers."""
    
    def __init__(self, arm_controller, mode='broadcast'):
        """
        Initialize leader controller.
        
        Args:
            arm_controller: ArmController instance
            mode: Either 'broadcast' (multiple followers) or 'single' (one follower)
        """
        self.arm = arm_controller
        self.mode = mode
        self.followers = []
        
    def configure_as_leader(self):
        """Configure the arm as a leader."""
        # Send ESP-NOW configuration command
        # Mode 1 for broadcast or Mode 2 for single follower
        pass
        
    def add_follower(self, mac_address):
        """
        Add a follower arm by MAC address.
        
        Args:
            mac_address: MAC address of the follower arm
        """
        # Send command to add follower
        pass
        
    def remove_follower(self, mac_address):
        """
        Remove a follower arm.
        
        Args:
            mac_address: MAC address of the follower arm
        """
        # Send command to remove follower
        pass
        
    def start_broadcasting(self):
        """Start broadcasting movements to followers."""
        # Enable broadcasting
        pass
        
    def stop_broadcasting(self):
        """Stop broadcasting movements to followers."""
        # Disable broadcasting
        pass
        
    def control_all_followers(self, joint_positions):
        """
        Send joint positions to all followers.
        
        Args:
            joint_positions: Dictionary of joint positions
        """
        # Send command to control all followers
        pass


class FollowerController:
    """Controls a follower arm that receives from a leader."""
    
    def __init__(self, arm_controller):
        """
        Initialize follower controller.
        
        Args:
            arm_controller: ArmController instance
        """
        self.arm = arm_controller
        
    def configure_as_follower(self, leader_mac):
        """
        Configure the arm as a follower.
        
        Args:
            leader_mac: MAC address of the leader arm
        """
        # Add leader MAC address
        # Set follower mode
        pass
        
    def get_status(self):
        """Get current follower status."""
        # Query follower status
        pass
```

### Perception System

#### `sam2/model.py`
```python
"""
Integration of SAM2 (Segment Anything Model v2) for object segmentation.

Research references:
- SAM2 Paper: /research/sam2-segment-anything-model.pdf
"""

class SAM2Segmenter:
    """Interface to the SAM2 model for segmentation."""
    
    def __init__(self, model_path, device='cuda'):
        """
        Initialize SAM2 model.
        
        Args:
            model_path: Path to pretrained model weights
            device: 'cuda' or 'cpu'
        """
        # Load SAM2 model
        pass
        
    def segment_image(self, image, prompt=None):
        """
        Segment objects in an image.
        
        Args:
            image: Input image (numpy array)
            prompt: Optional segmentation prompt (point, box, text)
            
        Returns:
            Dictionary of segmentation masks and metadata
        """
        # Preprocess image
        # Run SAM2 inference
        # Postprocess results
        pass
    
    def track_object(self, initial_mask, frames):
        """
        Track an object across video frames.
        
        Args:
            initial_mask: Initial segmentation mask
            frames: List of video frames
            
        Returns:
            List of masks for each frame
        """
        # Implement object tracking using SAM2
        pass
```

### Transformer-Based Encoder

#### `transformer/encoder.py`
```python
"""
BERT-like bidirectional transformer encoder for contextual embedding.

Research references:
- BERT Paper: /research/bert-paper.pdf
- Attention Is All You Need: /research/attention-is-all-you-need.pdf
"""

class BERTEncoder:
    """Bidirectional encoder with multi-head attention."""
    
    def __init__(self, input_dim, hidden_dim, num_heads, num_layers, dropout=0.1):
        """
        Initialize BERT-like encoder.
        
        Args:
            input_dim: Dimension of input features
            hidden_dim: Dimension of hidden representations
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
            dropout: Dropout probability
        """
        # Initialize transformer encoder
        # Create positional encoding
        # Initialize multi-head attention layers
        # Initialize feed-forward networks
        # Initialize layer normalization
        pass
        
    def encode(self, inputs, attention_mask=None):
        """
        Encode inputs into contextual embeddings.
        
        Args:
            inputs: Input tensor [batch_size, seq_len, input_dim]
            attention_mask: Optional mask for padding
            
        Returns:
            Contextual embeddings [batch_size, seq_len, hidden_dim]
        """
        # Apply positional encoding
        # Process through transformer layers with multi-head attention
        # Apply layer normalization
        # Return contextual embeddings
        pass
    
    def forward(self, sensor_data, robot_state, task_embedding=None):
        """
        Process multi-modal inputs into unified representation.
        
        Args:
            sensor_data: Dictionary of sensor readings (vision, IMU, etc.)
            robot_state: Current robot state (joint positions, velocities)
            task_embedding: Optional task specification embedding
            
        Returns:
            Unified contextual embedding
        """
        # Preprocess and concatenate inputs
        # Apply transformer encoding with multi-head attention
        # Return unified representation
        pass
```

#### `transformer/attention.py`
```python
"""
Multi-head attention implementation for parallel feature processing.

Research references:
- Attention Is All You Need: /research/attention-is-all-you-need.pdf
"""

class MultiHeadAttention:
    """Multi-head attention mechanism that processes different representation subspaces."""
    
    def __init__(self, embed_dim, num_heads, dropout=0.1):
        """
        Initialize multi-head attention module.
        
        Args:
            embed_dim: Dimension of input embedding
            num_heads: Number of attention heads
            dropout: Dropout probability
        """
        # Initialize query, key, value projections
        # Verify embed_dim is divisible by num_heads
        # Initialize output projection
        # Initialize dropout
        pass
        
    def split_heads(self, x, batch_size):
        """
        Split input tensor into multiple heads.
        
        Args:
            x: Input tensor [batch_size, seq_len, embed_dim]
            batch_size: Batch size
            
        Returns:
            Tensor with separated heads [batch_size, num_heads, seq_len, head_dim]
        """
        # Reshape tensor to [batch_size, seq_len, num_heads, head_dim]
        # Transpose to [batch_size, num_heads, seq_len, head_dim]
        pass
        
    def forward(self, query, key, value, mask=None):
        """
        Compute multi-head attention.
        
        Args:
            query: Query tensor [batch_size, query_len, embed_dim]
            key: Key tensor [batch_size, key_len, embed_dim]
            value: Value tensor [batch_size, value_len, embed_dim]
            mask: Optional attention mask
            
        Returns:
            Attention output [batch_size, query_len, embed_dim]
            Attention weights [batch_size, num_heads, query_len, key_len]
        """
        # Project inputs to query, key, value
        # Split heads
        # Compute scaled dot-product attention
        # Apply mask if provided
        # Apply softmax and dropout
        # Combine heads
        # Project to output dimension
        pass
```

### Active Inference

#### `active_inference/free_energy.py`
```python
"""
Implementation of free energy principle for active inference.

Research references:
- Free Energy Principle: /research/free-energy-principle.pdf
"""

class FreeEnergyMinimizer:
    """Implements free energy minimization for action selection."""
    
    def __init__(self, forward_model, precision=1.0):
        """
        Initialize free energy minimizer.
        
        Args:
            forward_model: Model that predicts future states
            precision: Precision parameter for weighting prediction errors
        """
        self.forward_model = forward_model
        self.precision = precision
        
    def compute_free_energy(self, current_state, action, desired_state):
        """
        Compute free energy for a given action.
        
        Args:
            current_state: Current robot state
            action: Proposed action
            desired_state: Desired outcome state
            
        Returns:
            Free energy value (lower is better)
        """
        # Predict next state using forward model
        # Compute prediction error between predicted and desired state
        # Weight by precision
        # Return free energy
        pass
    
    def select_action(self, current_state, desired_state, action_space):
        """
        Select action to minimize free energy.
        
        Args:
            current_state: Current robot state
            desired_state: Desired outcome state
            action_space: Available actions
            
        Returns:
            Selected action that minimizes free energy
        """
        # Evaluate free energy for each action
        # Return action with minimum free energy
        pass
    
    def update_beliefs(self, predicted_state, observed_state):
        """
        Update internal model based on prediction errors.
        
        Args:
            predicted_state: State predicted by forward model
            observed_state: Actually observed state
            
        Returns:
            Updated belief state
        """
        # Compute prediction error
        # Update model parameters to reduce error
        # Return updated belief state
        pass
```

### Training System

#### `co_training/action_chunking.py`
```python
"""
Implementation of action chunking for efficient execution.

Research references:
- Chain of Draft: /research/chain-of-draft.pdf
- Mobile ALOHA: /research/mobile-aloha.pdf
"""

class ActionChunker:
    """Chunks actions into efficient sequences."""
    
    def __init__(self, max_chunk_size=5, min_chunk_size=2):
        """
        Initialize action chunker.
        
        Args:
            max_chunk_size: Maximum number of actions per chunk
            min_chunk_size: Minimum number of actions per chunk
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        
    def identify_chunks(self, action_sequence):
        """
        Identify natural chunks in an action sequence.
        
        Args:
            action_sequence: Sequence of actions
            
        Returns:
            List of action chunks
        """
        # Analyze action sequence for patterns
        # Identify breakpoints between logical chunks
        # Return chunked sequence
        pass
    
    def optimize_chunks(self, chunks, execution_time):
        """
        Optimize chunks based on execution metrics.
        
        Args:
            chunks: List of action chunks
            execution_time: Execution time for each chunk
            
        Returns:
            Optimized chunks
        """
        # Analyze execution performance
        # Adjust chunk boundaries for efficiency
        # Return optimized chunks
        pass
    
    def execute_chunks(self, chunks, controller):
        """
        Execute chunks sequentially.
        
        Args:
            chunks: List of action chunks
            controller: Robot controller
            
        Returns:
            Execution results
        """
        # Execute each chunk as a unit
        # Monitor performance
        # Return results
        pass
```

## Implementation Roadmap

1. **Hardware Setup & Integration** (Phase 1)
   - Set up single RoArm-M3 Pro control
   - Configure and test leader-follower mode
   - Integrate RealSense camera and IMU
   - Test ODrive motor control

2. **Perception System Development** (Phase 1)
   - Implement SAM2 integration
   - Develop computer vision pipeline
   - Integrate and calibrate sensors
   - Test real-time performance

3. **Core AI Architecture** (Phase 2)
   - Implement BERT-like encoder
   - Develop forward model for state prediction
   - Implement free energy computation
   - Test with simulated data

4. **Mobile Base Integration** (Phase 2)
   - Integrate ODrive with mobile base
   - Implement navigation module
   - Test mobility with single arm pair
   - Optimize power management

5. **Training Pipeline** (Phase 3)
   - Implement imitation learning from demonstrations
   - Develop co-training strategy
   - Implement action chunking
   - Test with leader-follower arm pair

6. **Multi-Arm Coordination** (Phase 3)
   - Scale to four arms on training cart
   - Implement workspace management
   - Test collaborative tasks
   - Optimize coordination strategies

7. **Inference System** (Phase 4)
   - Develop multi-draft reasoning (Chain-of-Draft)
   - Implement task planning and decomposition
   - Test autonomous operation
   - Optimize for real-time performance

8. **System Integration & Testing** (Phase 4)
   - Full system integration
   - Comprehensive testing suite
   - Performance optimization
   - Documentation and refinement

## Git Workflow

```bash
# Create a new branch for a specific component
git checkout -b feature/component-name

# Make changes and commit regularly
git add .
git commit -m "Implement specific functionality"

# Push to GitHub with branch tracking
git push -u origin feature/component-name

# Create pull request for review
gh pr create --title "Feature: Component Name" --body "Description of changes"
```

## Research Integration References

For each module, the key research papers to reference:

- **Transformer Architecture**: `attention-is-all-you-need.pdf` - Foundation for multi-head attention mechanism
- **BERT Encoding**: `bert-paper.pdf` - Bidirectional context encoding
- **Active Inference**: `free-energy-principle.pdf` - Theoretical foundation for action selection
- **Multi-Draft Reasoning**: `chain-of-draft.pdf` - Iterative refinement for planning
- **Imitation Learning**: `mobile-aloha.pdf` - Leader-follower imitation approach
- **Computer Vision**: `sam2-segment-anything-model.pdf` - Visual segmentation
- **Reinforcement Learning**: `sim-to-real-reinforcement-learning.pdf` - Sim-to-real transfer
- **Test-Time Adaptation**: `titans-paper.pdf` - Memory utilization during inference
- **Activation Functions**: `relu-paper.pdf` - Neural network design