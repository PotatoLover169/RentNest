import Card from "./Card";

function EmptyState({
  title = "Nothing here yet",
  description,
  action,
}) {
  return (
    <Card className="p-10 text-center">
      <h2 className="text-lg font-semibold text-slate-950">
        {title}
      </h2>

      {description && (
        <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
          {description}
        </p>
      )}

      {action && <div className="mt-5">{action}</div>}
    </Card>
  );
}

export default EmptyState;