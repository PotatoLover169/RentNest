import Card from "./Card";

function ErrorState({
  title = "Something went wrong",
  message = "Unable to load this information.",
  action,
}) {
  return (
    <Card className="border-red-200 bg-red-50 p-6">
      <h2 className="text-lg font-semibold text-red-900">
        {title}
      </h2>

      <p className="mt-2 text-sm text-red-700">
        {message}
      </p>

      {action && <div className="mt-4">{action}</div>}
    </Card>
  );
}

export default ErrorState;