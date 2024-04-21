class DatabaseException(Exception):
    def __init__(self, message, func, query):
        self.message = f"Error in {func}, {message}.query: {query}"