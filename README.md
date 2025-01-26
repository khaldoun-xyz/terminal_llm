# simple script to talk to an LLM in your terminal

---

## set up

- create a .env file and provide the parameters `GROQ_API_KEY` and `MODEL`.
- create a virtualenv or conda environment
  using the requirements.txt file & activate it
- navigate to `src` & start chatting with `python chat.py -u <your_user_name>`

## alias as short cut

- if you want to jump right in with one command,
  open your .bashrc and set something like this:
  `alias talk='cd [PATH_TO_REPO]/src &&
  . ~/virtualenvs/[ENV_NAME]/bin/activate && python chat.py`
