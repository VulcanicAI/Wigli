# wigli _wigli_testutils.py

from appdirs import user_data_dir
from os.path import join
from pytest import raises
from typing import Callable, List

from wigli._wigli_cli import wigli_cli as wigli

TEST_DIR = join(".", "tests")


def get_test_dir():
    try:
        if isinstance(TEST_DIR, str):
            return TEST_DIR
    except BaseException:
        pass
    return user_data_dir(
        appname="TestWigli", appauthor="VulcanicAI"
    )


def cli_tester(
    argv_: str | List[str] or List[List[str]],
    response_assert: str | List[str] | Callable | None = None,
    out_assert: str | List[str] | Callable | None = None,
    err_assert: str | List[str] | Callable | None = None,
    expect_response: bool = True,
    raises_expectation=None,
    data_dir: str | None = None,
    verbosity: int = 0,
    capsys=None,
):
    if isinstance(argv_, str):
        argv_ = [argv_]
    if len(argv_) <= 0:
        return
    if isinstance(argv_[0], List):
        for arg in argv_:
            cli_tester(
                arg,
                response_assert=response_assert,
                out_assert=out_assert,
                err_assert=err_assert,
                expect_response=expect_response,
                raises_expectation=raises_expectation,
                data_dir=data_dir,
                verbosity=verbosity,
                capsys=capsys,
            )
        return

    if data_dir is not None:
        temp_dir = join(get_test_dir(), data_dir)
    else:
        temp_dir = join(get_test_dir(), "dynamic_data_dir")

    if raises_expectation is not None:
        with raises(raises_expectation) as e:
            wigli(
                argv_=argv_,
                data_dir=temp_dir,
                verbosity=verbosity,
            )
            assert e.value.code == 0
    else:
        wigli(
            argv_=argv_, data_dir=temp_dir, verbosity=verbosity
        )

    if capsys is not None:
        out, err = capsys.readouterr()
        if out_assert is not None:
            if isinstance(out_assert, str):
                a = out_assert.lower()
                b = out.lower()
                assert a in b
            elif isinstance(out_assert, Callable):
                assert out_assert(out.lower())
            else:
                for s in out_assert:
                    a = s.lower()
                    b = out.lower()
                    assert a in b
        if err_assert is not None:
            if isinstance(err_assert, str):
                a = err_assert.lower()
                b = err.lower()
                assert a in b
            elif isinstance(err_assert, Callable):
                assert err_assert(err.lower())
            else:
                for s in err_assert:
                    a = s.lower()
                    b = err.lower()
                    assert a in b
