"""
ProgramMind

数字孪生模型

Digital Twin


用于:

学生画像
教师画像
课程画像
知识画像


"""


import datetime



class DigitalTwin:



    def __init__(
        self,
        entity_id,
        entity_type
    ):


        self.profile={


            "id":
            entity_id,


            "type":
            entity_type,


            "create_time":
            str(datetime.datetime.now()),


            "data":{}


        }





    def update(
        self,
        key,
        value
    ):


        """
        更新画像数据
        """


        self.profile["data"][key]=value



        return self.profile





    def get_profile(self):


        return self.profile





# ==========================
# 学生数字孪生
# ==========================


class StudentTwin(DigitalTwin):


    def __init__(
        self,
        student_id
    ):


        super().__init__(

            student_id,

            "student"

        )



    def update_learning(
        self,
        kci,
        knowledge
    ):


        self.update(

            "KCI",

            kci

        )


        self.update(

            "knowledge",

            knowledge

        )





# ==========================
# 教师数字孪生
# ==========================


class TeacherTwin(DigitalTwin):


    def __init__(
        self,
        teacher_id
    ):


        super().__init__(

            teacher_id,

            "teacher"

        )



    def update_course(
        self,
        course
    ):


        self.update(

            "course",

            course

        )





# ==========================
# 课程数字孪生
# ==========================


class CourseTwin(DigitalTwin):


    def __init__(
        self,
        course_id
    ):


        super().__init__(

            course_id,

            "course"

        )





if __name__=="__main__":



    student=StudentTwin(
        "student001"
    )


    student.update_learning(

        85,

        {

        "Python":90,

        "算法":75

        }

    )


    print(

        student.get_profile()

    )