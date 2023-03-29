from contextlib import redirect_stdout
import io


f = io.StringIO()
with redirect_stdout(f):
    print("hello world!")
    f.truncate(0)
    f.seek(0)
    print("This is the second message")

print(f.getvalue())
print(f.getvalue())
