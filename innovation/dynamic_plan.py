"""
ProgramMind

动态学习规划模型


根据KCI指数

自动生成学生学习路线


"""


class DynamicPlanner:



    def __init__(self):


        pass




    def generate_plan(
        self,
        kci_data
    ):


        """
        输入:

        {

        KCI:65,

        weak_points:
        [
        "数据结构",
        "算法"
        ]

        }


        输出:

        学习计划


        """



        kci=kci_data.get(
            "KCI",
            0
        )


        weak=kci_data.get(

            "weak_points",

            []

        )



        plan=[]



        if kci<60:


            plan.append(

                "基础知识强化学习"

            )


        elif kci<80:


            plan.append(

                "知识理解与实践训练"

            )


        else:


            plan.append(

                "高级应用与科研探索"

            )





        for item in weak:


            plan.append(

                f"加强知识点:{item}"

            )



        return {


            "student_level":

            self.level(kci),


            "learning_plan":

            plan


        }




    def level(
        self,
        kci
    ):


        if kci>=85:


            return "高级"



        elif kci>=60:


            return "中级"



        else:


            return "初级"





    def update_plan(
        self,
        old_plan,
        new_kci
    ):


        """
        根据新KCI调整计划
        """


        new_plan=self.generate_plan(

            new_kci

        )


        return new_plan





if __name__=="__main__":



    planner=DynamicPlanner()



    result=planner.generate_plan(

        {

        "KCI":65,

        "weak_points":

        [

        "机器学习",

        "数据结构"

        ]

        }

    )



    print(result)