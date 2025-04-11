import sys
import mongoengine as me
from noppakao import models
import datetime
from flask_bcrypt import Bcrypt
import random

bcrypt = Bcrypt()


def create_user_admin():
    print("start create admin")
    user = models.User(
        username="admin",
        first_name="admin",
        last_name="system",
        status="active",
        phone_number="1234567890",
        email="admin@example.com",
        roles=["user", "admin"],
        password=bcrypt.generate_password_hash("p@ssw0rd"),
    )

    user.save()
    print("finish")
    return user


def check_has_user_admin_and_reset_pwd():
    print("Checking has user admin")
    user = models.User.objects(username="admin").first()
    if user:
        user.set_password("p@ssw0rd")
        user.save()
        print("There is a user admin.\nReset admin password: Done")
        return user
    return create_user_admin()


def create_organizations(admin):
    organizations = []
    for i in range(3):
        organization = models.Organization(
            name=f"School {i+1}", description=f"รายละเอียด {i+1}", created_by=admin
        )
        organization.save()
        organizations.append(organization)
    return organizations


def create_users(organizations):
    users = []
    for i in range(10):
        user = models.User(
            username=f"user{i+1}",
            first_name=f"first name {i+1}",
            last_name=f"last name {i+1}",
            status="active",
            phone_number="1234567890",
            email=f"testuser.{i+1}@example.com",
            roles=["user"],
            password=bcrypt.generate_password_hash(f"{i+1}" * 6),
            organization=random.choice(organizations),
        )
        user.save()
        users.append(user)
    return users


def create_event(admin):
    event = models.Event(
        code="000",
        name="Event Test",
        type="team",
        flag_prefix="CTF",
        started_date=datetime.datetime.now(),
        ended_date=datetime.datetime.now() + datetime.timedelta(days=1),
        register_started_date=datetime.datetime.now(),
        register_ended_date=datetime.datetime.now() + datetime.timedelta(days=1),
        publish_started_date=datetime.datetime.now(),
        created_by=admin,
        updated_by=admin,
    )
    event.save()
    return event


def create_categories(admin):
    categories = []
    for i in range(3):
        category = models.Category(
            name=f"category {i+1}",
            created_by=admin,
            updated_by=admin,
        )
        category.save()
        categories.append(category)
    return categories


def create_challenges(admin, categories):
    challenges = []
    for i in range(20):
        challenge = models.Challenge(
            name=f"challenge {i+1}",
            category=random.choice(categories),
            description=f"CTF{'{'+ str(i+1) +'}'}",
            hint=f"hint {i+1}",
            answer=f"{i+1}",
            answer_type="flag",
            created_by=admin,
            updated_by=admin,
        )
        challenge.save()
        challenges.append(challenge)
    return challenges


def create_teams(users):
    teams = []
    for i in range(4):
        if users:
            members = random.sample(users, 3) if len(users) > 3 else users
            users = [user for user in users if user not in members]
            team = models.Team(
                name=f"Team {i+1}",
                members=members,
                created_by=members[0],
                updated_by=members[0],
            )
            team.save()
            teams.append(team)

    return teams


def create_event_competitors(teams, event):
    event_competitors = []
    for team in teams:
        event_competitor = models.EventCompetitor(
            team=team,
            event=event,
            created_by=team.members[0],
            updated_by=team.members[0],
        )
        event_competitor.save()
        event_competitors.append(event_competitor)
    return event_competitors


def create_event_roles(teams, event):
    event_roles = []
    for team in teams:
        for member in team.members:
            event_role = models.EventRole(
                role="competitor",
                event=event,
                user=member,
                created_by=member,
                updated_by=member,
            )
            event_role.save()
            event_roles.append(event_role)
    return event_roles


def create_event_challenges(admin, challenges, event):
    event_challenges = []
    for challenge in challenges:
        score = random.choice([100, 200, 300, 400, 500])
        event_challenge = models.EventChallenge(
            event=event,
            challenge=challenge,
            first_blood_score=score * 2,
            success_score=score,
            hint_score=-(int(score / 4)),
            fail_score=-(int(score / 1)),
            created_by=admin,
            updated_by=admin,
        )
        event_challenge.save()
        event_challenges.append(event_challenge)
    return event_challenges


if __name__ == "__main__":
    if len(sys.argv) > 1:
        me.connect(db="noppakaodb", host=sys.argv[1])
    else:
        me.connect(db="noppakaodb")
    print("start create")

    admin = check_has_user_admin_and_reset_pwd()

    organizations = create_organizations(admin)
    users = create_users(organizations)

    event = create_event(admin)
    categories = create_categories(admin)
    challenges = create_challenges(admin, categories)

    teams = create_teams(users)
    event_competitors = create_event_competitors(teams, event)
    event_roles = create_event_roles(teams, event)

    event_challenges = create_event_challenges(admin, challenges, event)

    print("end create")
