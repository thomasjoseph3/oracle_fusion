import { useRef, useEffect } from "react";

export default function Table({ data }) {
    const tableRef = useRef(null);
    const { columns, rows } = data;

    console.log({ columns, rows }); 

    useEffect(() => {
        if (tableRef.current) {
            tableRef.current.style.width = tableRef.current.scrollWidth + "px";
        }
    }, []);

    return (
        <div ref={tableRef} className="relative shadow-md sm:rounded-lg overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-500">
                <thead className="text-xs text-gray-700 uppercase bg-[#F7F7F7E5]">
                    <tr>
                        {columns.map((col, index) => (
                            <th key={`col-${index}-${col || 'unknown'}`} className="px-6 py-3">
                                {col || "Unknown Column"}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="text-gray-700">
                    {rows.map((row, rowIndex) => (
                        <tr key={`row-${rowIndex}`} className="odd:bg-[#dedede] even:bg-[#F7F7F7E5]">
                            {row.map((cell, cellIndex) => {
                                const columnKey = columns[cellIndex] || `unknown-${cellIndex}`;
                                return (
                                    <td key={`cell-${rowIndex}-${columnKey}`} className="px-6 py-4">
                                        {cell}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
