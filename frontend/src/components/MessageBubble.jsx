export default function MessageBubble({ role, content }) {
	const isUser = role === "user";

	return (
		<div
			style={{
				display: "flex",
				justifyContent: isUser ? "flex-end" : "flex-start",
				marginBottom: "10px",
			}}
		>
			<div
				style={{
					maxWidth: "80%",
					padding: "10px 12px",
					borderRadius: "10px",
					background: isUser ? "#daf1ff" : "#f2f2f2",
					border: "1px solid #ddd",
					whiteSpace: "pre-wrap",
				}}
			>
				{content}
			</div>
		</div>
	);
}
