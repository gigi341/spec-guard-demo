from fastapi import APIRouter, HTTPException

router = APIRouter()

fake_users = {
    1: {"id": 1, "name": "Alice"},
    2: {"id": 2, "name": "Bob"},
}

@router.get("/users/{user_id}")
def get_user(user_id: int):
    user = fake_users.get(user_id)

    # Intentional contradiction:
    # README says missing users return 404,
    # but implementation returns 500.
    if user is None:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    return user