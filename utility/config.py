from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    print(parser.sections())
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def create_db_url():
    params = config()
    host = params["host"]
    db = params["database"]
    user = params["user"]
    password = params["password"]
    return f"postgresql+asyncpg://{user}:{password}@{host}:5432/{db}"