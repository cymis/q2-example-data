import nox
from nox.sessions import Session

nox.options.sessions = ["test", "lint"]


@nox.session(venv_backend="none")
def test(session: Session) -> None:
    session.run("python", "-m", "pytest", "tests", *session.posargs, external=True)


@nox.session(venv_backend="none")
def lint(session: Session) -> None:
    session.run("ruff", "check", ".", external=True)


@nox.session(venv_backend="none")
def typecheck(session: Session) -> None:
    session.run("pyright", ".", external=True)


@nox.session(venv_backend="none")
def cov(session: Session) -> None:
    session.run("coverage", "run", "-m", "pytest", "tests", external=True)
    session.run("coverage", "report", "-m", external=True)
