"""
ProgramMind

KCI知识掌握可信指数模型

Knowledge Confidence Index

用于:
学生知识掌握程度评估


核心思想:

KCI =
理论测试
+
实践表现
+
知识迁移
+
复习情况
+
学习行为


"""


class KCIModel:



    def __init__(self):


        # 权重配置

        self.weights={

            "test":0.30,

            "practice":0.25,

            "transfer":0.20,

            "review":0.15,

            "behavior":0.10

        }




    def calculate(
        self,
        data
    ):

        """
        计算KCI


        输入:

        {

        test:90,

        practice:80,

        transfer:75,

        review:85,

        behavior:90

        }


        输出:

        {

        kci:84.5,

        level:"优秀"

        }


        """



        score=0



        for key,weight in self.weights.items():


            value=data.get(
                key,
                0
            )


            score += value * weight




        score=round(
            score,
            2
        )



        return {


            "KCI":score,

            "level":
            self.level(score)


        }




    def level(
        self,
        score
    ):


        if score>=90:


            return "优秀"



        elif score>=75:


            return "良好"



        elif score>=60:


            return "一般"



        else:


            return "需要加强"





    def knowledge_analysis(
        self,
        knowledge_scores
    ):


        """
        多知识点掌握分析


        输入:

        {
        Python:90,
        数据结构:70
        }

        """


        result={}



        for k,v in knowledge_scores.items():


            result[k]={


                "score":v,


                "status":
                self.level(v)


            }



        return result





if __name__=="__main__":


    model=KCIModel()



    student={


        "test":90,

        "practice":85,

        "transfer":80,

        "review":90,

        "behavior":85

    }



    print(

        model.calculate(
            student
        )

    )