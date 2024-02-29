from orm import Model, CharField, MigrationManager, DataBaseConnector


if __name__=="__main__":
    class User(Model):
        _table_name = "user_table"

        name = CharField(primary_key=True, max_length=20)
        fav_food = CharField(max_length=150, null=True)

    class Test(Model):
        _table_name = "test_table"

        test_name = CharField(primary_key=True, max_length=20)
        test_food = CharField(max_length=150, null=True)

    # database connector
    connection = DataBaseConnector("my_test_db")
    u = User()
    migration_manager = MigrationManager([User, Test])
    migration_manager.apply(connection=connection)
    # # migration_manager.apply()

