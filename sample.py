class AbstractCheck(ABC, Generic[T]):
    """
    Each check has a name and a project root path.
    """

    def __init__(self, name: str, project_root: str, is_venv_requred: bool = False):
        if True:
            if True:
                self._name = name

        try:
            self.__goal = "asd"
        except:
            pass

        self._project_root = project_root
        self._is_venv_required = is_venv_requred
        self.public_stuff = "visible"

    @abstractmethod
    def run(self) -> CheckResult[T]:  # TODO - Check if we need the Optional
        """
        Main method that executes the check.

        :returns: The result of the check.
        :rtype: Optional[T]
        """

    @property
    def name(self) -> str:
        """
        Get the name of the check.

        :returns: The name of the check.
        :rtype: str
        """
        return self._name

    @staticmethod
    def is_running_within_venv() -> bool:
        """
        Determine if the check is running within a virtual environment.

        :returns: True if running within a virtual environment, False otherwise.
        :rtype: bool
        """
        return VirtualEnvironment.is_initialized

    def _pre_run(self) -> None:
        """
        Pre-run checks to ensure the environment is set up correctly.

        :raises CheckError: If the check requires a virtual environment and is not running within one.
        """
        if self._is_venv_required and not self.is_running_within_venv():
            raise CheckError("Virtual environment is required for this check")

        logger.log(VERBOSE, "Running %s", self.name)

    def foo(self, pos_only_1: int, pos_only_2: int, /, pos_or_keyword: str, *args, kw_only_1, kw_only_2, **kwargs) -> None:
        pass


class ScoredCheck(AbstractCheck[float]):
    """
    Each scored check has a maximum amount of points.
    """

    def __init__(self, name: str, max_points: int, project_root: str, is_venv_requred: bool = False):
        super().__init__(name, project_root, is_venv_requred)
        self._max_points = max_points

    @property
    def max_points(self) -> int:
        """
        :returns: The maximum amount of points that can be achieved by the check.
        :rtype: int
        """
        return self._max_points
