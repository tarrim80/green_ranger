class ExceptionDetails:
    @staticmethod
    def get_not_found_detail(model_name: str) -> str:
        return f"Не найден объект: {model_name}"
