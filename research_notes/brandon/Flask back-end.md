# Overview
Supports both user input and chart-based output for differential diagnosis

- **Routing and APIs:** Flask manages user interactions through API end- points. User responses to medical questions are sent as POST requests and formatted for model input. 
- **Data Processing:** Input data is validated and transformed using regular expressions before being passed to the neural network.
- **Model Inference:** The fine-tuned LLM runs on a GPU-enabled server, and Flask orchestrates model inference and session management.
# See also
- [[Web-based Interface]]
# Source
- https://arxiv.org/abs/2506.19702