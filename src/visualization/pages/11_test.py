from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st
from src.visualization.components.layout import initialize_page
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import AgentExecutor, create_tool_calling_agent
import json
from langchain_core.tools import tool

def load_db(embeddings):
    return FAISS.load_local('data/faiss_store', embeddings, allow_dangerous_deserialization=True)


st.set_page_config(page_title="GEEK Token アナリティクス",
                    page_icon="📊",
                    layout="wide")

initialize_page()

def get_mcp_tools():
    with open("mcp_config.json", "r") as f:
        config = json.load(f)
    mcp_client = MultiServerMCPClient(config["mcpServers"])
    tools = mcp_client.get_tools()
    return tools

@tool
def get_rag_tools(llm, prompt):
    """
     Last Memorysの背景情報を参照して質問に回答するツール

    Args:
        llm (str): 使用するLLM
        prompt (str): 質問

    Returns:
        Dict[str, Optional[str]]: {
            "result": 回答,
            "source_documents": 参考元
        }
    """ 
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    db = load_db(embeddings)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True
    )
    return qa_chain.invoke(prompt)

def get_tools(llm, prompt):
    return get_mcp_tools() + get_rag_tools(llm, prompt)

def main():
    # LLMの初期化
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        max_retries=2,
    )

    # オリジナルのSystem Instructionを定義する
    system_prompt_template = SystemMessagePromptTemplate.from_template("""
    あなたは、「Last Memorys」というブロックチェーンゲーム専用のチャットボットです。
    ゲームに精通したプレイヤーになりきって、背景情報を参考に質問に回答してくだい。
    情報がなければ、その内容については言及しないでください。
    """)
# 「Last Memorys」に全く関係のない質問と思われる質問に関しては、「ゲームに関係ない質問には答えられません。」と答えてください。

    human_message_prompt = HumanMessagePromptTemplate.from_template("""
    以下の背景情報を参照してください。
    # 背景情報
    {context}

    # 質問
    {question}
    """)

    prompt = ChatPromptTemplate.from_messages([system_prompt_template, human_message_prompt])


    # Agentの初期化
    agent = create_tool_calling_agent(
            llm=llm,
            tools=get_tools(llm, prompt),
            prompt=prompt
        )
    
    # Agentの実行
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=get_tools(llm, prompt),
        verbose=True,
        max_iterations=3
    )

    if "messages" not in st.session_state:
      st.session_state.messages = []
    if user_input := st.chat_input('質問しよう！'):
        # 以前のチャットログを表示
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        print(user_input)
        with st.chat_message('user'):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message('assistant'):
            with st.spinner('Lasmem bot is typing ...'):
                response = agent_executor.invoke({"input": user_input})
            st.markdown(response['result'])
            #参考元を表示
            doc_urls = []
            for doc in response["source_documents"]:
                #既に出力したのは、出力しない
                if doc.metadata["source_url"] not in doc_urls:
                    doc_urls.append(doc.metadata["source_url"])
                    st.markdown(f"参考元：{doc.metadata['source_url']}")
        st.session_state.messages.append({"role": "assistant", "content": response["result"]})



main()
