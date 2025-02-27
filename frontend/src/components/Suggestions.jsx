/* eslint-disable react/prop-types */
const Suggestions = ({
  suggestions,
  loader,
  handleSuggestionClick,
  selectedSuggestion,
}) => {
  if (!suggestions || suggestions.length === 0) return null;

  // List of suggestions that should be disabled
  const disabledSuggestions = [
    "Try a different query !!!",
    "Check your internet connection !!!",
    "Use simpler keywords !!!",
  ];

  if (suggestions === null) {
    suggestions = disabledSuggestions;
  }

  // ✅ Properly clean suggestions
  const cleanedSuggestions = suggestions.map((s) =>
    s.replace(/^"/, "").replace(/",?$/, "")
  );

  return (
    <div className="grid grid-cols-2 gap-2 h-auto rounded-lg p-2 m-2 overflow-hidden">
      {cleanedSuggestions?.slice(0, 3).map((suggestion, index) => {
        const isDisabled = loader || disabledSuggestions.includes(suggestion); // Disable condition

        return (
          <div
            key={index}
            onClick={() => !isDisabled && handleSuggestionClick(suggestion)} // Prevent click when disabled
            className={`p-2 bg-gray-100 rounded-full flex items-center justify-center text-center overflow-hidden text-sm cursor-pointer transition duration-200 ${
              isDisabled
                ? "opacity-50 pointer-events-none cursor-not-allowed"
                : ""
            } ${
              selectedSuggestion === suggestion
                ? "bg-blue-300"
                : "hover:bg-blue-200"
            } ${index === 2 ? "col-span-2" : ""}`}
          >
            <span className="block w-full">{suggestion}</span>
          </div>
        );
      })}
    </div>
  );
};

export default Suggestions;
