# Overview
The Streamlit session_state object stores the values of variables that persist across reruns of your Streamlit app. It's essentially a dictionary that holds the state of your application.

Here's a breakdown of the types of information you can store:
- User inputs: Anything the user enters in widgets (sliders, text inputs, etc.)
- Application state: Values that define the current state of your app (e.g., whether a file has been uploaded).
- Session data: Data associated with the user's session.
- Calculated values: Results of computations that don't need to be recalculated on every rerun.

Example:
session_state.user_input = "Hello, world!"

IMPORTANT: session_state is automatically reset on every rerun of the app.

You must explicitly update it in your Streamlit code.
# See also
- [[Streamlit]]
# Source
