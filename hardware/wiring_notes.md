# Wiring Notes

Keep measurement channels isolated and labeled:

- `v_input`: supply voltage at driver input.
- `i_input`: supply current into driver.
- `v_coil`: voltage across active coil or EML channel.
- `i_coil`: current through active coil or EML channel.
- `v_recovery`: flyback/recovery path voltage.
- `i_recovery`: flyback/recovery path current.

Do not combine supply input and recovered flyback energy in one channel. The
audit needs gross input, recovered energy, and net input as separate values.

Use twisted pairs or coax where appropriate, keep high-current switching loops
short, and keep sensor grounds documented.
