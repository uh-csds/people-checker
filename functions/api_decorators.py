# general_api.py
# Functions (currently only decorators) useful for designing API classes.

def check_correct_api(link):
    """Makes sure that an API's link is correct on input, else returns an error."""
    def decorator(func):
        def wrapper(base_api, *args, **kwargs):
            if base_api.get_url() != link:
                return f"Error: Invalid base url. For this function, your url should be {link}."
            return func(base_api, *args, **kwargs)
        return wrapper
    return decorator

def check_correct_argument(desired_argument, arguments_keyword, partial=False):
    """Makes sure that a classes list of arguments contains a desired argument. Useful for making sure an APIClass method that desires a specific argument does not contain any others. Can search either exactly or partially."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            arguments = getattr(self, arguments_keyword)
            for arg in arguments:
                if not partial and desired_argument == arg:
                    return func(self, *args, **kwargs)
                elif partial and desired_argument in arg:
                    return func(self, *args, **kwargs)
            return f"Error: Desired argument {desired_argument} not found in {arguments}. Check to make sure your arguments have been set up correctly."
        return wrapper
    return decorator
