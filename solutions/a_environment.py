

@app.get('/db')
async def run_select(session: Annotated[AsyncSession, Depends(db.get_session)]):
    await session.execute(text('select 1'))
