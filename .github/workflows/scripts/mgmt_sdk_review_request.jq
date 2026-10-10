def envelope:
  {request: ({operation: $operation, draft: .} | tojson)};

if $operation != "check" and $operation != "preflight" then
  error("Only check and preflight requests can be bounded")
else
  # Include JSON string escaping, not just the unwrapped draft's byte count.
  until(
    (envelope | tojson | utf8bytelength) <= 9000 or
    ([.packages[].attribution | length] | add // 0) == 0;
    ([.packages | to_entries[] | select(.value.attribution | length > 0) | .key] | last) as $index
    | .packages[$index].attribution |= .[:-1]
    | .packages[$index].attribution_omitted += 1
  )
  | if (envelope | tojson | utf8bytelength) > 9000 then
      error("Checks and findings exceed the 9000-byte MCP request budget even without attribution; report incomplete")
    else
      envelope
    end
end
