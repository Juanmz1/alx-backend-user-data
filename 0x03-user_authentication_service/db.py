#!/usr/bin/env python3
""" creating the db storage """


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from user import Base, User  # Assuming User model is defined in a 'user.py' file

class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the database

        Args:
            email (str): User's email
            hashed_password (str): Hashed password

        Returns:
            User: Newly added user object
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user


    def find_user_by(self, **kwargs) -> User:
        """Find a user by the specified filter criteria

        Args:
            **kwargs: Arbitrary keyword arguments for filtering

        Returns:
            User: User object matching the filter criteria

        Raises:
            NoResultFound: If no results are found
            InvalidRequestError: If wrong query arguments are passed
        """
        try:
            user = self._session.query(User).filter_by(**kwargs).first()
            if not user:
                raise NoResultFound("No user found with the specified filter criteria")
            return user
        except InvalidRequestError as e:
            raise InvalidRequestError("Invalid query arguments") from e

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user's attributes based on the provided arguments

        Args:
            user_id (int): User ID to update
            **kwargs: Arbitrary keyword arguments for updating user attributes

        Returns:
            None

        Raises:
            ValueError: If an invalid argument is passed
        """
        try:
            user = self.find_user_by(id=user_id)
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                else:
                    raise ValueError(f"Invalid attribute: {key}")
            self._session.commit()
        except (NoResultFound, InvalidRequestError):
            raise ValueError(f"User with ID {user_id} not found")

