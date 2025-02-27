import { useMessages } from "../context/MessageContext";
import axios from "axios";

const useQueryExecutor = () => {
  const { setMessages, setLoader } = useMessages();

  const executeQuery = async (query) => {
    if (!query.trim()) return;
    
    setLoader(true);
    setMessages((prev) => prev.filter((msg) => !msg.error)); // Remove errors before request

    try {
      setLoader(true);
      const response = await axios.post(
        "http://192.168.1.55:5000/generate-and-execute",
        // "https://demo-oracle.updations.com/generate-and-execute",
        { prompt: query, show_suggestion: true, show_description: true }
      );


      const { execution_result } = response.data;

      if (
        execution_result?.columns?.length <= 0 ||
        execution_result?.rows?.length <= 0
      ) {
        setMessages((prev) => [
          {
            user: false,
            no_data: true,
            text: "No data found. try the suggestions...",
            suggestions: response?.data?.suggestions,
          },
          ...prev,
        ]);
      } else {

        const botResponse = {
          user: false,
          question: query,
          description: response?.data?.description,
          suggestions: response?.data?.suggestions,
          table:
            response?.data?.type === "table" &&
            execution_result?.columns &&
            execution_result?.rows
              ? execution_result
              : null,
          graph:
            response?.data?.type === "graph" &&
            execution_result?.columns &&
            execution_result?.rows
              ? execution_result
              : null,
          text:
            response?.data.type === "text" &&
            execution_result?.columns &&
            execution_result?.rows
              ? execution_result
              : null,
        };

        setMessages((prev) => [botResponse, ...prev]);
      }
      setLoader(false);
    }catch (error) {
      console.error("Error fetching data:", error);
      
      setMessages((prev) => [
        {
          user: false,
          error: true,
          text: "Something went wrong. Please try again.",
          suggestions:error.response.data.suggestions
        },
        ...prev
      ]);
    }

    setLoader(false);
  };

  return { executeQuery };
};

export default useQueryExecutor;
