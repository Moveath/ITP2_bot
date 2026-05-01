class UserSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.source_text = ""
        self.question_count = 5
        self.language = "Русский"
        self.level = "Средний"
        self.questions = []
        self.answers = []
        self.current_index = 0
