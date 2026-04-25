# App Testing Checklist — v1.1.0

- [ ] Create and activate virtual environment.
- [ ] Install requirements.
- [ ] Initialize database with `python setup/init_db.py`.
- [ ] Start API with `bash setup/run.sh api`.
- [ ] Start Streamlit with `bash setup/run.sh ui`.
- [ ] Test a core complaint flow.
- [ ] Confirm constant pattern skips episode-duration.
- [ ] Confirm ROS batch proceeds to the next system block when more ROS questions remain.
- [ ] Confirm extracted state is readable.
- [ ] Confirm template summary renders.
- [ ] Optional: set `ANTHROPIC_API_KEY` and confirm AI summary generation.
- [ ] Optional: run Ollama fallback.
- [ ] Run `bash setup/run_tests.sh`.
