from aiogram.fsm.state import State, StatesGroup

class PhotoStates(StatesGroup):
    waiting_for_enhance = State()
    waiting_for_removebg = State()
    waiting_for_edit_text = State()
    waiting_for_edit_prompt = State()
    waiting_for_gemini_question = State()
    waiting_for_gemini_image = State()