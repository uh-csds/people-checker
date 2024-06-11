# general_api.py
# Functions (currently only decorators) useful for designing API classes.

def check_correct_link(link):
    """Makes sure that a link is correct on input, else returns an error.
    :param link: Desired API link to check."""
    def decorator(func):
        def wrapper(base_api, *args, **kwargs):
            if base_api.get_url() != link:
                raise ValueError(f"Invalid url. For this function, your url should be {link}.")
            return func(base_api, *args, **kwargs)

        return wrapper

    return decorator


def check_correct_argument(desired_argument, arguments_keyword, partial=False):
    """Makes sure that a classes list of arguments contains a desired argument. Useful for making sure an APIClass
    method that desires a specific argument does not contain any others. Can search either exactly or partially.
    :param partial: If False, sees if desired_argument equals an arg in arguments_keyword exactly. If True,
    sees if it is in an arg in arguments_keyword.
    :param arguments_keyword: Arguments to search (expects dictionary).
    :param desired_argument: Argument to find."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            arguments = getattr(self, arguments_keyword)
            for arg in arguments:
                if not partial and desired_argument == arg:
                    return func(self, *args, **kwargs)
                elif partial and desired_argument in arg:
                    return func(self, *args, **kwargs)
            raise KeyError(f"Desired argument {desired_argument} not found in {arguments}. Check to make sure your arguments have been set up correctly.")

        return wrapper

    return decorator
