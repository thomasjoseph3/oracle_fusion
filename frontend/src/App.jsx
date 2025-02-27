import { useState } from "react";
import "./App.css";
import BeatLoader from "react-spinners/BeatLoader";
import { useMessages } from "./context/MessageContext";
import Component from "./Component.jsx";
import useQueryExecutor from "./hooks/useQueryExecutor";

const App = () => {
  const { messages, loader } = useMessages();

  const [suggestions] = useState([
    "Show me the financial transactions recorded in 2024",
    "What is the total weight being transported by all trolleys assigned to Rail R042?",
    "Which vessels do we have in the database?",
  ]);
  const [query, setQuery] = useState("");
  const { executeQuery } = useQueryExecutor();

  const handleSuggestionClick = (suggestion) => {
    executeQuery(suggestion, false); //  Execute query on suggestion click
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  const handleSend = () => {
    executeQuery(query, true);
    setQuery("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <div className="bg-gradient-to-b from-blue-50 to-white">
      <div className="flex justify-between px-6 py-3">
        <p className="text-black text-opacity-40 text-[16px] font-medium">
          DEMO - AI Data Analysis Platform
        </p>
        <svg
          className="cursor-pointer"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M5.85 17.1C6.7 16.45 7.65 15.9375 8.7 15.5625C9.75 15.1875 10.85 15 12 15C13.15 15 14.25 15.1875 15.3 15.5625C16.35 15.9375 17.3 16.45 18.15 17.1C18.7333 16.4167 19.1875 15.6417 19.5125 14.775C19.8375 13.9083 20 12.9833 20 12C20 9.78333 19.2208 7.89583 17.6625 6.3375C16.1042 4.77917 14.2167 4 12 4C9.78333 4 7.89583 4.77917 6.3375 6.3375C4.77917 7.89583 4 9.78333 4 12C4 12.9833 4.1625 13.9083 4.4875 14.775C4.8125 15.6417 5.26667 16.4167 5.85 17.1ZM12 13C11.0167 13 10.1875 12.6625 9.5125 11.9875C8.8375 11.3125 8.5 10.4833 8.5 9.5C8.5 8.51667 8.8375 7.6875 9.5125 7.0125C10.1875 6.3375 11.0167 6 12 6C12.9833 6 13.8125 6.3375 14.4875 7.0125C15.1625 7.6875 15.5 8.51667 15.5 9.5C15.5 10.4833 15.1625 11.3125 14.4875 11.9875C13.8125 12.6625 12.9833 13 12 13ZM12 22C10.6167 22 9.31667 21.7375 8.1 21.2125C6.88333 20.6875 5.825 19.975 4.925 19.075C4.025 18.175 3.3125 17.1167 2.7875 15.9C2.2625 14.6833 2 13.3833 2 12C2 10.6167 2.2625 9.31667 2.7875 8.1C3.3125 6.88333 4.025 5.825 4.925 4.925C5.825 4.025 6.88333 3.3125 8.1 2.7875C9.31667 2.2625 10.6167 2 12 2C13.3833 2 14.6833 2.2625 15.9 2.7875C17.1167 3.3125 18.175 4.025 19.075 4.925C19.975 5.825 20.6875 6.88333 21.2125 8.1C21.7375 9.31667 22 10.6167 22 12C22 13.3833 21.7375 14.6833 21.2125 15.9C20.6875 17.1167 19.975 18.175 19.075 19.075C18.175 19.975 17.1167 20.6875 15.9 21.2125C14.6833 21.7375 13.3833 22 12 22ZM12 20C12.8833 20 13.7167 19.8708 14.5 19.6125C15.2833 19.3542 16 18.9833 16.65 18.5C16 18.0167 15.2833 17.6458 14.5 17.3875C13.7167 17.1292 12.8833 17 12 17C11.1167 17 10.2833 17.1292 9.5 17.3875C8.71667 17.6458 8 18.0167 7.35 18.5C8 18.9833 8.71667 19.3542 9.5 19.6125C10.2833 19.8708 11.1167 20 12 20ZM12 11C12.4333 11 12.7917 10.8583 13.075 10.575C13.3583 10.2917 13.5 9.93333 13.5 9.5C13.5 9.06667 13.3583 8.70833 13.075 8.425C12.7917 8.14167 12.4333 8 12 8C11.5667 8 11.2083 8.14167 10.925 8.425C10.6417 8.70833 10.5 9.06667 10.5 9.5C10.5 9.93333 10.6417 10.2917 10.925 10.575C11.2083 10.8583 11.5667 11 12 11Z"
            fill="black"
            fillOpacity="0.4"
          />
        </svg>
      </div>
      <div className="min-h-screen p-6 flex flex-col items-center justify-center">
        {!messages[0] && (
          <>
            <div className="flex flex-col justify-center items-center mb-24">
              <h1 className="text-2xl font-bold mb-3">Welcome back!</h1>
              <p className="font-semibold">To start analysing ,ask your own question</p>
            </div>
            <div className="flex w-full max-w-3xl space-x-4 items-stretch mb-4">
              {suggestions?.map((suggestion, index) => (
                <div
                  className="flex-1 bg-white text-center p-4 rounded-lg shadow-md font-semibold text-sm"
                  style={{ color: "#1B75BC" }}

                  key={suggestion + index}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          </>
        )}
        <div className="mt-6 w-full max-w-3xl flex items-center bg-white shadow-md rounded-lg overflow-hidden px-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your question here..."
            className="w-full  py-3 outline-none text-base"
          />
          <div>
            {loader && (
              <svg
                className="pointer-events-none"
                width="30"
                height="30"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M5.55567 26.011C5.18522 26.1592 4.83333 26.1278 4.5 25.9167C4.16667 25.7055 4 25.4 4 25V18.5557L14.2667 16L4 13.4V6.99999C4 6.59999 4.16667 6.29443 4.5 6.08332C4.83333 5.87221 5.18522 5.84077 5.55567 5.98899L26.889 14.9667C27.3408 15.1667 27.5667 15.5111 27.5667 16C27.5667 16.4889 27.3408 16.8333 26.889 17.0333L5.55567 26.011Z"
                  fill="#575B5F"
                  fillOpacity="0.5"
                />
              </svg>
            )}

            {!loader && (
              <svg
                onClick={handleSend}
                className="cursor-pointer"
                width="30"
                height="30"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M5.55567 26.011C5.18522 26.1592 4.83333 26.1278 4.5 25.9167C4.16667 25.7055 4 25.4 4 25V18.5557L14.2667 16L4 13.4V6.99999C4 6.59999 4.16667 6.29443 4.5 6.08332C4.83333 5.87221 5.18522 5.84077 5.55567 5.98899L26.889 14.9667C27.3408 15.1667 27.5667 15.5111 27.5667 16C27.5667 16.4889 27.3408 16.8333 26.889 17.0333L5.55567 26.011Z"
                  fill="#1B75BC"
                />
              </svg>
            )}
          </div>
        </div>
        {loader && (
          <div className="pt-10">
            <BeatLoader color="#2877BD" size={10} margin={4} />
          </div>
        )}

        {messages.length > 0 &&
          messages.map((message, index) => (
            <Component key={`msg-${index}-${message.text}`} message={message} />
          ))}
      </div>
    </div>
  );
};

export default App;
