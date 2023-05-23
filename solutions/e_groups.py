Session = async_sessionmaker(expire_on_commit=False)


async def create_group(
    session: AsyncSession, group_in: serializers.GroupIn
) -> models.Group:
    group = models.Group(name=group_in.name)
    if group_in.members:
        group.members = await repositories.users.get_by_ids(session, group_in.members)
    session.add(group)
    return group


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    members: Mapped[list['User']] = relationship(
        back_populates='groups', secondary='memberships', lazy='joined'
    )


async def get_by_id(session: AsyncSession, group_id: int) -> models.Group | None:
    # statement = (
    #     select(models.Group)
    #     .where(models.Group.id == group_id)
    #     .options(joinedload(models.Group.members))
    # )
    # return await session.scalar(statement)
    return await session.get(models.Group, group_id)
