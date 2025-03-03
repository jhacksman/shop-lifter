# shop-lifter
A toy implementation of the shoppie concept, using Waveshare RoArm-M3 5+1DoF Pro robotic arms

## Key Technologies

### Active Inference
A biologically inspired framework that continuously minimizes prediction errors (or free energy) to adapt actions in uncertain environments. It offers a more natural, brain-like way for robots to learn and make decisions.

### ReLU (Rectified Linear Unit)
A simple yet powerful activation function (f(x)=max(0,x)) that supports efficient, non-linear transformations within neural networks. Its simplicity helps maintain fast, stable training, which is essential for complex systems.

### Multi-Head Attention
A mechanism from transformer architectures that allows the system to focus on different aspects of multi-modal inputs (like video and sensor data) simultaneously. By processing various "heads" in parallel, it builds a rich, contextual embedding of the environment.

When you integrate these elements—with an encoder-decoder architecture that fuses camera data, IMU readings, and other sensor inputs, and then predicts future joint positions—the result is a system capable of complex motion planning. Human demonstrations and performance grading further refine this process, ultimately guiding the robot toward ideal, context-aware behavior.

Together, these technologies promise a new generation of robots that can perceive, adapt, and act with human-like intuition and robustness.

## Prompt

```
You are tasked with generating a modular code framework in Python that implements an efficient active inference system inspired by both Chain-of-Draft and Mobile ALOHA. The framework should include:

1. A BERT-like bidirectional transformer encoder that processes past observations to generate contextual embeddings. Use ReLU (or a variant) as the activation function.
2. A forward model module that takes these embeddings and predicts future state matrices.
3. An active inference module that computes a free energy (or surprise) metric based on the difference between predicted and actual states, and implements an optimization loop to minimize this metric.
4. Efficiency strategies:
   - Co-training: Include support for pre-training the forward model using a static dataset as well as live/demo data.
   - Action Chunking: Implement a mechanism to predict and execute sequences of actions in a "chunked" fashion to reduce latency.
5. The code should be organized in a modular project structure with separate folders or modules for:
   - Model definitions (e.g., `models/transformer.py`, `models/forward_model.py`, `models/active_inference.py`)
   - Training and evaluation pipelines (e.g., `train.py`, `evaluate.py`)
   - Utilities and configuration (e.g., `utils/`, `config.py`)
   - Unit tests for each module (e.g., using `pytest`)
6. Ensure that best coding practices are followed, with clear docstrings, inline comments, and thorough unit tests for each component.

Include in your output the complete source code with inline comments and docstrings, and a README that explains how to run the code and how the modules interact. Also, add the full URLs of the following reference materials as comments at the top of your code:
   - Chain-of-Draft: https://arxiv.org/abs/2502.18600
   - Mobile ALOHA: https://mobile-aloha.github.io
   - Free Energy Principle / Active Inference: https://en.wikipedia.org/wiki/Free_energy_principle and https://arxiv.org/html/2412.14741v1
   - BERT Paper: https://doi.org/10.48550/arXiv.1810.04805
   - Transformer Overview: https://blogs.nvidia.com/blog/what-is-a-transformer-model/
   - ReLU Activation Function: https://en.wikipedia.org/wiki/Rectifier_(neural_networks)
   - Titans: Learning to Memorize at Test Time: https://arxiv.org/abs/2501.00663

Generate the code in small, testable pieces with detailed comments, starting with the model definition modules. The solution should be comprehensive enough to serve as a starting framework for further development.
```
