# Standard
import os

# Third Party
import nox

nox.options.reuse_existing_virtualenvs = True

nox.options.sessions = "lint", "tests", "fmt", "proto3"

python_versions = ["3.8", "3.9", "3.10", "3.11"]


@nox.session(python=python_versions)
def tests(session):
    """run tests with pytest and coverage"""
    session.install(".[all,dev-test]")

    name = session.python.replace(".", "")

    posargs = ("-m", "not examples") if not session.posargs else session.posargs
    session.run(
        "pytest",
        "--cov=caikit",
        f"--cov-report=html:coverage-{name}",
        f"--cov-report=xml:coverage-{name}.xml",
        f"--html=durations/{name}.html",
        *posargs,
    )


@nox.session(reuse_venv=False)
def docs(session):
    session.install(".[dev-docs]")

    with session.chdir(os.path.join("docs", "source")):
        session.run("sphinx-build", "-E", "-a", "-b", "html", "-T", ".", "_build/html")


@nox.session
def fmt(session: nox.Session) -> None:
    """format with pre-commit"""
    session.install("pre-commit")

    try:
        session.run(
            "pre-commit",
            "run",
            "--all-files",
        )
    except nox.command.CommandFailed:
        ci = os.getenv("CI")

        if ci and ci == "true":
            warning = (
                "This test failed because your code isn't formatted correctly.\n"
                "Locally, run `make run fmt`, it will appear to fail, but change files.\n"
                "Add the changed files to your commit and this stage will pass.\n"
            )
        else:
            warning = (
                "☝️ This appears to have failed, but actually your files have been formatted.\n"
                "Make a new commit with these changes before making a pull request."
            )

        print(
            "\033[1;33m",  # light yellow
            warning,
            "\033[0m",  # reset
        )
        raise


@nox.session
def lint(session: nox.Session) -> None:
    """lint with pylint"""
    session.install("-e", ".[all,dev-fmt,dev-test]")

    session.run(
        "pylint",
        "caikit",
        "examples/text-sentiment/text_sentiment",
        "examples/text-sentiment/*.py",
        "examples/sample_lib/*.py",
        *session.posargs,
    )


@nox.session
def imports(session: nox.Session) -> None:
    """enforce internal import rules"""
    session.install("-e", ".")
    session.install("pydeps")

    session.run(
        "./scripts/check_deps.sh",
        external=True,
    )


@nox.session
def build(session: nox.Session) -> None:
    """build wheel"""
    session.install("flit==3.9.0")

    session.run(
        "flit",
        "build",
        env={
            "FLIT_USERNAME": "__token__",
        },
    )


@nox.session
def publish(session: nox.Session) -> None:
    """publish wheel to PyPI"""
    session.install("flit==3.9.0")

    session.run(
        "flit",
        "publish",
        env={
            "FLIT_USERNAME": "__token__",
        },
    )


@nox.session(python=["3.8"])
def proto3(session: nox.Session) -> None:
    """run tests with protobuf 3.X to ensure compatibility"""
    session.install("-e", ".[all,dev-test]")

    session.install(
        "protobuf==3.19.0",
        "grpcio-health-checking",
        "grpcio-reflection",
    )

    posargs = ("-m", "not examples") if not session.posargs else session.posargs

    session.run(
        "pytest",
        "--cov=caikit",
        "--cov-report=html",
        *posargs,
    )


@nox.session(python=python_versions)
def core(session: nox.Session) -> None:
    """run tests against caikit.core without any extras"""
    session.install("-e", ".[dev-test]")

    session.run(
        "pytest",
        "tests/core",
    )


@nox.session
def dsconverter(session: nox.Session) -> None:
    """convert docstrings to google by running dsconverter"""
    session.install("-e", ".[all,dev-test]")

    session.run(
        "python",
        "./scripts/dsconverter.py",
        "caikit",
    )
