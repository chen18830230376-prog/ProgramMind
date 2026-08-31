"""
ProgramMind

PostgreSQL业务数据库管理


保存:

1. 用户信息
2. 学习行为
3. 数字孪生数据
4. 课程信息



数据库:

PostgreSQL


"""



import psycopg2

from psycopg2.extras import RealDictCursor





class PostgreSQLManager:



    def __init__(

        self,

        host="localhost",

        port=5432,

        database="programmind",

        user="postgres",

        password="123456"

    ):


        self.config={


            "host":host,

            "port":port,

            "database":database,

            "user":user,

            "password":password


        }


        self.conn=None





    # =====================
    # 数据库连接
    # =====================


    def connect(self):


        """

        建立数据库连接

        """


        try:


            self.conn=psycopg2.connect(

                **self.config

            )


            print(

                "PostgreSQL连接成功"

            )


            return self.conn



        except Exception as e:


            print(

                "数据库连接失败:",

                e

            )


            return None





    # =====================
    # 创建数据表
    # =====================


    def create_tables(self):


        """

        创建ProgramMind业务表


        """


        sql="""

        CREATE TABLE IF NOT EXISTS students(

            id SERIAL PRIMARY KEY,

            student_id VARCHAR(100),

            name VARCHAR(100),

            kci FLOAT,

            profile JSONB

        );



        CREATE TABLE IF NOT EXISTS courses(

            id SERIAL PRIMARY KEY,

            course_id VARCHAR(100),

            name VARCHAR(200),

            description TEXT

        );



        CREATE TABLE IF NOT EXISTS learning_records(


            id SERIAL PRIMARY KEY,


            student_id VARCHAR(100),


            knowledge VARCHAR(200),


            score FLOAT,


            create_time TIMESTAMP DEFAULT NOW()


        );


        """



        cursor=self.conn.cursor()


        cursor.execute(sql)


        self.conn.commit()



        cursor.close()



        print(

            "业务表创建完成"

        )






    # =====================
    # 保存学生画像
    # =====================


    def save_student_profile(

        self,

        student_id,

        name,

        kci,

        profile

    ):


        sql="""

        INSERT INTO students

        (

        student_id,

        name,

        kci,

        profile

        )


        VALUES

        (%s,%s,%s,%s)

        """



        cursor=self.conn.cursor()



        cursor.execute(

            sql,

            (

            student_id,

            name,

            kci,

            profile

            )

        )


        self.conn.commit()


        cursor.close()





    # =====================
    # 查询学生
    # =====================


    def get_student(

        self,

        student_id

    ):


        sql="""

        SELECT *

        FROM students

        WHERE student_id=%s

        """



        cursor=self.conn.cursor(

            cursor_factory=RealDictCursor

        )


        cursor.execute(

            sql,

            (

            student_id,

            )

        )


        result=cursor.fetchone()


        cursor.close()


        return result






if __name__=="__main__":


    db=PostgreSQLManager()


    db.connect()