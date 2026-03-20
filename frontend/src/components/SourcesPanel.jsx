export default function SourcesPanel({ sources = [] }) {
	return (
		<aside style={{ width: "280px", border: "1px solid #ddd", borderRadius: "8px", padding: "12px", height: "fit-content" }}>
			<h3 style={{ marginTop: 0 }}>Sources</h3>
			{sources.length === 0 ? (
				<p style={{ margin: 0, color: "#666" }}>No sources yet.</p>
			) : (
				<ul style={{ margin: 0, paddingLeft: "18px" }}>
					{sources.map((source, index) => (
						<li key={index} style={{ marginBottom: "6px", wordBreak: "break-word" }}>
							{typeof source === "string" ? source : JSON.stringify(source)}
						</li>
					))}
				</ul>
			)}
		</aside>
	);
}
