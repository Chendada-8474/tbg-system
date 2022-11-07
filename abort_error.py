import traceback
import sys


def abort_msg(e):
    """500 bad request for exception

    Returns:
        500 and msg which caused problems
    """
    error_class = e.__class__.__name__  # 引發錯誤的 class
    detail = e.args[0]  # 得到詳細的訊息
    cl, exc, tb = sys.exc_info()  # 得到錯誤的完整資訊 Call Stack
    last_call_stack = traceback.extract_tb(tb)[-1]  # 取得最後一行的錯誤訊息
    file_name = last_call_stack[0]  # 錯誤的檔案位置名稱
    line_num = last_call_stack[1]  # 錯誤行數
    func_name = last_call_stack[2]  # function 名稱
    # generate the error message
    error_message = "Exception raise in file:\n{}\n line {}\n in {}: [{}] {}.".format(
        file_name, line_num, func_name, error_class, detail
    )
    # return 500 code
    return error_message
