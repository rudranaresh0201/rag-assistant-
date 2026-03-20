import { useState } from "react";

export default function InputBox({ onSend, isLoading }) {
	const [query, setQuery] = useState("");

	const handleSubmit = (event) => {
		event.preventDefault();
		if (isLoading) {
			return;
		}

		const text = query.trim();
		if (!text) {
			return;
		}

		onSend(text);
		setQuery("");
	};

	return (
		<form onSubmit={handleSubmit} style={{ display: "flex", gap: "8px" }}>
			<input
				type="text"
				value={query}
				onChange={(event) => setQuery(event.target.value)}
				placeholder="Type your question..."
				disabled={isLoading}
				style={{ flex: 1, padding: "10px", borderRadius: "6px", border: "1px solid #ccc" }}
			/>
			<button
				type="submit"
				disabled={isLoading}
				style={{ padding: "10px 14px", borderRadius: "6px", border: "1px solid #ccc", cursor: "pointer" }}
			>
				Send
			</button>
		</form>
	);
}
