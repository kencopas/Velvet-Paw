import inspect
import os


# Retrieves an environment variable, logs if it doesn't exist
def gotenv(varname: str):
    envvar = os.getenv(varname)
    if not envvar:
        print(f"Missing required environment variable: {varname}")
    return envvar


def path_log(message: str, err: Exception = None) -> None:
    """
    This function logs a message in the console, but prepends the function name
    as would be referenced statically. Function/method's are logged as follows:

    - function_name | message
    - class_name.method_name | message
    """

    frame_info = inspect.stack()[1]
    frame = frame_info.frame
    func_name = frame_info.function

    # Try to get class name if 'self' or 'cls' is in local variables
    cls_name = None
    if 'self' in frame.f_locals:
        cls_name = type(frame.f_locals['self']).__name__
    elif 'cls' in frame.f_locals:
        cls_name = frame.f_locals['cls'].__name__

    method_name = f"{cls_name}.{func_name}" if cls_name else func_name

    print(f"{method_name} | {message}")
    if err:
        print(f"{type(err).__name__}: {err}")


def debug(func):
    def wrapper(*args, **kwargs):
        read_kwargs = [f"{key}={val}" for key, val in kwargs.items()]
        print(
            f"\n{func.__name__}({', '.join([str(a) for a in args])},"
            f"{', '.join(read_kwargs)})\n"
        )
        return func(*args, **kwargs)
    return wrapper
