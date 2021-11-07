class SqlQueries:
    stg_events_table_create = ("""
    DROP TABLE IF EXISTS stg_events;

    CREATE TABLE IF NOT EXISTS stg_events
    (
        artist varchar NULL,
        auth varchar NULL,
        firstname varchar NULL,
        gender varchar NULL,
        iteminsession bigint NULL,
        lastname varchar NULL,
        length decimal NULL,
        level varchar NULL,
        location varchar NULL,
        method varchar NULL,
        page varchar NULL,
        registration decimal NULL,
        sessionid int NULL,
        song varchar NULL,
        status int NULL,
        ts bigint NULL,
        useragent varchar NULL,
        userid int NULL
    );
    """)
    
    stg_songs_table_create = ("""
    DROP TABLE IF EXISTS stg_songs;

    CREATE TABLE IF NOT EXISTS stg_songs
    (
        num_songs int NULL,
        artist_id varchar NULL,
        artist_latitude decimal NULL,
        artist_longitude decimal NULL,
        artist_name varchar NULL, 
        song_id varchar NOT NULL,
        title varchar NULL,
        duration decimal NULL,
        year int NULL
    );
    """)
    
    songplay_table_create = ("""
    DROP TABLE IF EXISTS songplay;
    
    CREATE TABLE IF NOT EXISTS songplay 
    (
        songplay_id int NOT NULL GENERATED ALWAYS AS IDENTITY,
        start_time timestamp NULL,
        user_id varchar NOT NULL,
        level varchar NULL,
        song_id varchar NOT NULL,
        artist_id varchar NOT NULL,
        session_id varchar NOT NULL,
        location varchar NULL,
        user_agent varchar NULL
    );
    """)
    
    user_table_create = ("""
    DROP TABLE IF EXISTS dim_user;
    
    CREATE TABLE IF NOT EXISTS dim_user
    (
        user_id int NOT NULL PRIMARY KEY,
        first_name varchar NULL,
        last_name varchar NULL,
        gender varchar NULL,
        level varchar NULL
    );
    """)
    
    song_table_create = ("""
    DROP TABLE IF EXISTS dim_song;
    
    CREATE TABLE IF NOT EXISTS dim_song
        (
        song_id varchar NOT NULL PRIMARY KEY,
        title varchar NULL,
        artist_id varchar NOT NULL,
        year int NULL,
        duration decimal NULL
        );
    """)

    # Create table for artists in the song data (dimension table)
    artist_table_create = ("""
    DROP TABLE IF EXISTS dim_artist;
    
    CREATE TABLE IF NOT EXISTS dim_artist
        (
        artist_id varchar NOT NULL PRIMARY KEY,
        artist_name varchar NULL,
        artist_location varchar NULL,
        artist_latitude decimal NULL,
        artist_longitude decimal NULL
        );
    """)

    # Create table for start times and date information from log data (dimension table)
    time_table_create = ("""
    DROP TABLE IF EXISTS dim_time;
    
    CREATE TABLE IF NOT EXISTS dim_time
        (
        start_time varchar NOT NULL PRIMARY KEY,
        hour int NOT NULL,
        day int NOT NULL,
        week int NOT NULL,
        month int NOT NULL,
        year int NOT NULL,
        weekday int NOT NULL
        );
    """)
    
    songplay_table_insert = ("""
    INSERT INTO songplay
    (
        start_time,
        user_id,
        level,
        song_id,
        artist_id,
        session_id,
        location,
        user_agent
    )
        SELECT
                events.start_time, 
                events.userid, 
                events.level, 
                songs.song_id, 
                songs.artist_id, 
                events.sessionid, 
                events.location, 
                events.useragent
                FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
            FROM stg_events
            WHERE page='NextSong') events
            LEFT JOIN stg_songs songs
            ON events.song = songs.title
                AND events.artist = songs.artist_name
                AND events.length = songs.duration
            WHERE songs.song_id IS NOT NULL
    """)

    user_table_insert = ("""
    INSERT INTO dim_user
        SELECT 
            distinct userid,
            firstname,
            lastname,
            gender,
            level
        FROM stg_events
        WHERE page='NextSong'
    """)

    song_table_insert = ("""
    INSERT INTO dim_song
        SELECT 
            distinct song_id,
            title,
            artist_id,
            year,
            duration
        FROM stg_songs
    """)

    artist_table_insert = ("""
    INSERT INTO dim_artist
        SELECT
            DISTINCT s.artist_id,
            s.artist_name,
            e.location,
            s.artist_latitude,
            s.artist_longitude
        FROM stg_songs as s
        JOIN stg_events as e
        ON s.artist_name = e.artist
    """)

    time_table_insert = ("""
    INSERT INTO dim_time
        SELECT 
            start_time,
            extract(hour from start_time),
            extract(day from start_time),
            extract(week from start_time), 
            extract(month from start_time),
            extract(year from start_time),
            extract(dayofweek from start_time)
        FROM songplay
    """)
