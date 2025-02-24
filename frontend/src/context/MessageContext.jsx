/* eslint-disable react/prop-types */
import { createContext, useContext, useState } from "react";

const MessageContext = createContext();

export const MessageProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [loader, setLoader] = useState(false);

  return (
    <MessageContext.Provider value={{ messages, setMessages, loader, setLoader }}>
      {children}
    </MessageContext.Provider>
  );
};

export const useMessages = () => useContext(MessageContext);
