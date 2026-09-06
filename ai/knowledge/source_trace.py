"""
ProgramMind

知识溯源模块


"""


class SourceTracer:



    def trace(

        self,

        retrieval_results

    ):



        sources=[]



        for item in retrieval_results:


            sources.append(

                {


                "document":

                item.get(

                    "source"

                ),


                "score":

                item.get(

                    "score"

                )

                }

            )



        return sources