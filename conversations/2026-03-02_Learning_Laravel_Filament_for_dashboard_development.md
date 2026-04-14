# Learning Laravel Filament for dashboard development
**Created:** 2026-03-02 12:59  |  **Updated:** 2026-03-02 18:32
**Composer ID:** `45d89c34-578f-4857-8f50-5f6fb20addf5`

---
### AI  ``

# Laravel + Filament Fundamentals

## 1. Laravel: Core Concepts

### MVC (Model–View–Controller)

| Layer | Role | Where it lives |
|-------|------|----------------|
| **Model** | Data and business logic | `app/Models/` |
| **View** | HTML / UI | `resources/views/` |
| **Controller** | Handles requests, calls models, returns views | `app/Http/Controllers/` |

Filament mostly replaces controllers with its own classes (Pages, Resources, Widgets).

---

### Request flow

```
HTTP Request → routes/web.php → Controller/Route
                                    ↓
                              Model (database)
                                    ↓
                              View (Blade template)
                                    ↓
                              HTML Response
```

---

### Directory structure (what matters)

```
app/
├── Models/           # Data models (Eloquent)
├── Http/Controllers/ # Request handlers
├── Filament/        # Filament-specific code
│   ├── Pages/       # Custom pages
│   ├── Resources/   # CRUD resources
│   └── Widgets/     # Dashboard widgets
config/              # App, DB, services config
database/
├── migrations/      # Schema changes
└── seeders/         # Test data
resources/
├── views/           # Blade templates
└── css/, js/        # Frontend assets
routes/
├── web.php          # Web routes
└── api.php          # API routes
```

---

## 2. Eloquent (ORM)

### Model basics

```php
// app/Models/Device.php
class Device extends Model
{
    protected $table = 'devices';      // Table name (optional if plural of class)
    protected $connection = 'supabase'; // DB connection
    protected $fillable = ['serial_number', 'status']; // Mass assignment
}
```

### Common queries

```php
// All records
Device::all();

// With conditions
Device::where('status', 'PASSED')->get();
Device::whereBetween('created_at', [$start, $end])->get();

// Single record
Device::find(1);
Device::where('serial_number', 'ABC123')->first();

// Count
Device::count();
Device::where('status', 'PASSED')->count();

// Aggregates
Device::avg('some_column');
Device::sum('some_column');
```

### Relationships

```php
// One device has many tests
class Device extends Model
{
    public function frequencyTests()
    {
        return $this->hasMany(FrequencyTest::class, 'serial_number', 'serial_number');
    }
}

// One test belongs to one device
class FrequencyTest extends Model
{
    public function device()
    {
        return $this->belongsTo(Device::class, 'serial_number', 'serial_number');
    }
}
```

### Raw SQL when needed

```php
DB::connection('supabase')->select('SELECT * FROM my_view WHERE id = ?', [1]);
DB::table('devices')->whereRaw('status = ?', ['PASSED'])->get();
```

---

## 3. Blade templates

### Syntax

```blade
{{-- Comments (not in output) --}}

{{ $variable }}              {{-- Escaped output --}}
{!! $html !!}                {{-- Raw HTML (use carefully) --}}

@if ($condition)
    ...
@elseif ($other)
    ...
@else
    ...
@endif

@foreach ($items as $item)
    {{ $item->name }}
@endforeach

@for ($i = 0; $i < 10; $i++)
    {{ $i }}
@endfor
```

### Layouts and sections

```blade
{{-- layout.blade.php --}}
<html>
<body>
    @yield('content')
</body>
</html>

{{-- page.blade.php --}}
@extends('layout')
@section('content')
    <h1>My Page</h1>
@endsection
```

### Components (Filament style)

```blade
<x-filament::card>
    <x-slot:heading>Title</x-slot:heading>
    Content here
</x-filament::card>
```

---

## 4. Filament: Core concepts

### Three main building blocks

| Type | Purpose | Example |
|------|---------|---------|
| **Resource** | CRUD for a model | DeviceResource → list/create/edit devices |
| **Page** | Custom page | Dashboard, Timeline Explorer |
| **Widget** | Reusable UI block | Stats card, chart |

---

### Resource (CRUD)

A Resource defines how a model is listed, created, and edited.

```php
// Conceptually
class DeviceResource extends Resource
{
    protected static ?string $model = Device::class;

    public static function form(Form $form): Form
    {
        return $form->schema([
            TextInput::make('serial_number')->required(),
            Select::make('status')->options([...]),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table->columns([
            TextColumn::make('serial_number'),
            TextColumn::make('status'),
        ]);
    }
}
```

- **Form** = create/edit form fields  
- **Table** = list view columns, filters, actions  

---

### Page (custom screen)

A Page is a full screen you control yourself.

```php
class TimelineExplorer extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-magnifying-glass';
    protected static string $view = 'filament.pages.timeline-explorer';

    public function getTitle(): string
    {
        return 'Timeline Explorer';
    }
}
```

- `$view` = Blade file for the page  
- You can add form fields, tables, widgets, etc.  
- Data comes from properties and methods you define  

---

### Widget (stats, charts, blocks)

Widgets are small UI blocks, often used on dashboards.

```php
class DeviceCountWidget extends StatsOverviewWidget
{
    protected function getStats(): array
    {
        return [
            Stat::make('Total Devices', Device::count()),
            Stat::make('Passed', Device::where('status', 'PASSED')->count()),
        ];
    }
}
```

Types:

- **StatsOverviewWidget** – stat cards  
- **ChartWidget** – charts  
- **TableWidget** – tables  
- **Widget** – custom HTML  

---

### Form components

```php
TextInput::make('name')->required()
Select::make('status')->options(['A' => 'Active', 'B' => 'Inactive'])
DatePicker::make('date')
Checkbox::make('is_active')
Textarea::make('notes')
```

---

### Table components

```php
TextColumn::make('serial_number')->searchable()->sortable()
BadgeColumn::make('status')->colors(['success' => 'PASSED', 'danger' => 'FAILED'])
IconColumn::make('status')->boolean()
```

---

### Actions (buttons)

```php
// On a form
Action::make('save')->action(fn () => $this->save())

// On a table row
Action::make('view')->url(fn ($record) => route('...', $record))
```

---

## 5. Data flow in Filament

### Page with form

```
User submits form
    → Filament validates
    → Your action/method runs
    → You update model / call service
    → Redirect or show message
```

### Page with table

```
Page loads
    → Filament builds query from table definition
    → Applies filters, search, sort
    → Renders table
```

### Widget

```
Dashboard loads
    → Each widget’s getStats() / getData() runs
    → Widget renders
```

---

## 6. PHP basics (for Laravel/Filament)

### Variables and types

```php
$name = 'John';
$count = 42;
$items = [1, 2, 3];
$obj = new SomeClass();
```

### Arrays

```php
$arr = ['a', 'b', 'c'];
$assoc = ['key' => 'value'];
$arr[] = 'new';           // Append
$assoc['new_key'] = 123;
```

### Functions and closures

```php
function myFunc($arg) {
    return $arg * 2;
}

$closure = fn($x) => $x * 2;  // Arrow function
$closure = function ($x) { return $x * 2; };
```

### Null safety

```php
$value = $obj?->property ?? 'default';  // Null-safe + default
```

### Collections (Laravel)

```php
$items = collect([1, 2, 3]);
$items->map(fn($x) => $x * 2);
$items->filter(fn($x) => $x > 1);
$items->pluck('name');
```

---

## 7. Common patterns

### Caching

```php
$data = Cache::remember('key', 300, function () {
    return ExpensiveQuery::get();
});
```

### Service classes

```php
// app/Services/OperatorDashboardService.php
class OperatorDashboardService
{
    public function getLeaderboard(string $filter): Collection
    {
        return DB::connection('supabase')
            ->select('SELECT * FROM get_operator_leaderboard(?)', [$filter]);
    }
}
```

### Dependency injection

```php
public function __construct(
    private OperatorDashboardService $service
) {}
```

---

## 8. Mental model

| Concept | Laravel | Filament |
|---------|---------|----------|
| Data | Eloquent models | Same models |
| List + CRUD | Controller + views | Resource |
| Custom screen | Controller + view | Page |
| Dashboard block | Partial / component | Widget |
| Form | Manual HTML/Blade | Form schema |
| Table | Manual HTML/Blade | Table schema |

---

## 9. Quick reference

| Task | Where / How |
|------|-------------|
| Define data structure | `app/Models/` |
| List + edit a model | Resource |
| Custom screen | Page + Blade view |
| Stat cards / charts | Widget |
| DB connection | `config/database.php` + `.env` |
| Routes | `routes/web.php` |
| Config | `config/*.php` |
| Logs | `storage/logs/laravel.log` |

If you want to go deeper, say which part: Eloquent, Blade, Resources, Pages, or Widgets.

---
### USER  ``

tech me one by one 
in laravel how to connect my current my code to supabase

---
### USER  ``

@c:\Users\pc\Downloads\dashboard 
hi cursor go through all the codes and information that is there in all the .md files 

i want some of the to get done

basically im a project manager i know python  and very good at software building 
so we have created a fqc app from where we are storing the data in supabase  

now we have selected laravel filament php to create a dashboad where we hve to show the raw information stored in the supa base in to meaning ful information such as time taken by the operator to assemble 
in a give time span how many device are doe things like this 

so to start with i only made by developwe do the app so i know in and out of it and i also know about the supabase querring and stuff 
but i have 0 knowledge on php and how to create web dashboard 
now i need you to teach me filament php laravel how it workes what are the basic cammands to get the inforamtion show the information create the template create the calculation etc 
im a very fast learner i want to know the fundamentals and what kinds of eror might happen and how we can diagnose it and tackle it

---
### USER  ``

dont worry about this 
What the dashboard should show

teach ne Laravel + Filament: Fundamentals 
i done want information on installing that ill make the operator do it

---
### USER  ``

@c:\Users\pc\Downloads\dashboard 
hi cursor go through all the codes and information that is there in all the .md files 

i want some of the to get done

basically im a project manager i know python  and very good at software building 
so we have created a fqc app from where we are storing the data in supabase  

now we have selected laravel filament php to create a dashboad where we hve to show the raw information stored in the supa base in to meaning ful information such as time taken by the operator to assemble 
in a give time span how many device are doe things like this 

so to start with i only made by developwe do the app so i know in and out of it and i also know about the supabase querring and stuff 
but i have 0 knowledge on php and how to create web dashboard 
now i need you to teach me filament php laravel how it workes what are the basic cammands to get the inforamtion show the information create the template create the calculation etc 
im a very fast learner i want to know the fundamentals and what kinds of eror might happen and how we can diagnose it and tackle it 

i want to chat and understand 
so using agent first u understand everything and then u teach me 

thes/md files are createdd by my previouse temmate when she was developing the same dashboard now we are doing the same  dashboard but using different supabase records so

---
### AI  ``

Exploring the dashboard folder and reading all .md files and code to understand the project.

---
### AI  ``

# Connecting Laravel to Supabase (Step by Step)

---

## Step 1: What You Need From Supabase

Supabase is PostgreSQL. You need:

1. **Host** – Supabase project host (often the pooler URL)
2. **Port** – usually `5432`
3. **Database** – usually `postgres`
4. **Username** – often `postgres.[project-ref]` for the pooler
5. **Password** – your project password

Where to find them:

- Supabase Dashboard → **Project Settings** → **Database**
- Use the **Connection pooling** (Transaction or Session) host if you have IPv6 issues

---

## Step 2: Add Credentials to `.env`

Create or edit `.env` in your Laravel project root:

```env
# Option A: Single connection (replace default DB)
DB_CONNECTION=pgsql
DB_HOST=aws-0-[region].pooler.supabase.com
DB_PORT=5432
DB_DATABASE=postgres
DB_USERNAME=postgres.abcdefghijklmnop
DB_PASSWORD=your_actual_password
DB_SSLMODE=require
```

Notes:

- `DB_HOST` – use the **pooler** host (e.g. `aws-0-ap-southeast-2.pooler.supabase.com`)
- `DB_USERNAME` – for pooler: `postgres.[project-ref]` (with the dot)
- `DB_SSLMODE=require` – Supabase needs SSL

If your password has special characters, URL-encode them:

| Character | Encoded |
|-----------|---------|
| `@`       | `%40`   |
| `#`       | `%23`   |
| `$`       | `%24`   |
| `%`       | `%25`   |
| `&`       | `%26`   |

---

## Step 3: Use a Separate Supabase Connection (Recommended)

Keep your default DB (e.g. SQLite for local) and add a second connection for Supabase.

**1. In `.env`:**

```env
# Default (e.g. local SQLite)
DB_CONNECTION=sqlite
DB_DATABASE=/absolute/path/to/database.sqlite

# Supabase (extra connection)
SUPABASE_HOST=aws-0-ap-southeast-2.pooler.supabase.com
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USERNAME=postgres.abcdefghijklmnop
SUPABASE_PASSWORD=your_password
SUPABASE_SSLMODE=require
```

**2. In `config/database.php`:**

Find the `connections` array and add:

```php
'connections' => [
    // ... sqlite, mysql, etc. ...

    'supabase' => [
        'driver' => 'pgsql',
        'url' => env('DATABASE_URL'),
        'host' => env('SUPABASE_HOST', '127.0.0.1'),
        'port' => env('SUPABASE_PORT', '5432'),
        'database' => env('SUPABASE_DATABASE', 'postgres'),
        'username' => env('SUPABASE_USERNAME', 'postgres'),
        'password' => env('SUPABASE_PASSWORD', ''),
        'charset' => 'utf8',
        'prefix' => '',
        'prefix_indexes' => true,
        'search_path' => 'public',
        'sslmode' => env('SUPABASE_SSLMODE', 'require'),
    ],
],
```

---

## Step 4: Use the Connection in Models

Tell each model which connection to use:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class FrequencyTest extends Model
{
    protected $connection = 'supabase';  // Use Supabase, not default DB
    
    protected $table = 'frequency_tests';
    
    protected $fillable = ['serial_number', 'operator_name', 'result', 'entry_timestamp'];
}
```

Without `protected $connection = 'supabase'`, Laravel uses the default connection.

---

## Step 5: Use the Connection in Queries

**Eloquent:**

```php
// Uses model's connection
$tests = FrequencyTest::where('result', 'PASS')->get();

// Or specify connection explicitly
$tests = FrequencyTest::on('supabase')->where('result', 'PASS')->get();
```

**Query builder:**

```php
use Illuminate\Support\Facades\DB;

$results = DB::connection('supabase')
    ->table('frequency_tests')
    ->where('result', 'PASS')
    ->get();
```

**Raw SQL:**

```php
$results = DB::connection('supabase')
    ->select('SELECT * FROM frequency_tests WHERE result = ?', ['PASS']);
```

**Calling a PostgreSQL function:**

```php
$leaderboard = DB::connection('supabase')
    ->select('SELECT * FROM get_operator_leaderboard(?)', ['Week']);
```

---

## Step 6: Test the Connection

**1. Clear config cache:**

```bash
php artisan config:clear
```

**2. Test in Tinker:**

```bash
php artisan tinker
```

Then:

```php
// Test 1: Get PDO
DB::connection('supabase')->getPdo();
// If no error, connection works

// Test 2: Simple query
DB::connection('supabase')->table('frequency_tests')->limit(1)->get();
// Should return rows or empty collection

// Test 3: Via model
App\Models\FrequencyTest::limit(1)->get();
```

---

## Step 7: Common Issues

| Issue | Likely cause | What to do |
|-------|--------------|------------|
| Connection refused | Wrong host/port | Use pooler host, port 5432 |
| Authentication failed | Wrong username/password | Check `postgres.[ref]` format, URL-encode password |
| SSL required | Missing SSL | Add `DB_SSLMODE=require` or `SUPABASE_SSLMODE=require` |
| IPv6 problems | Local network | Prefer pooler host (often IPv4) |
| Config not updating | Cached config | Run `php artisan config:clear` |

---

## Step 8: Optional – Use `DATABASE_URL`

Instead of separate env vars, you can use a single URL:

```env
SUPABASE_URL=postgresql://postgres.abcdefghijklmnop:your_password@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres?sslmode=require
```

Then in `config/database.php`:

```php
'supabase' => [
    'driver' => 'pgsql',
    'url' => env('SUPABASE_URL'),
    // ... rest can be minimal
],
```

---

## Summary

1. Get host, port, database, username, password from Supabase.
2. Add them to `.env` (or use `SUPABASE_URL`).
3. Add a `supabase` connection in `config/database.php`.
4. Set `protected $connection = 'supabase'` on models that use Supabase.
5. Use `DB::connection('supabase')` for raw/query builder.
6. Test with `php artisan tinker` and `DB::connection('supabase')->getPdo()`.

If you tell me your exact Supabase host format (e.g. `aws-0-xx.pooler.supabase.com`) and whether you use `.env` or `DATABASE_URL`, I can give you a copy-paste config tailored to your setup.

---
### AI  ``

Here’s a concise summary of what I learned from the docs and how it maps to Laravel + Filament.

---

# What I Understood From Your Project

## Your setup

1. **FQC Android app** → stores data in Supabase (PostgreSQL)
2. **Laravel + Filament** → dashboard that reads from Supabase and shows analytics
3. **Your role** → project manager, strong in Python and software, new to PHP
4. **Docs** → written by a previous teammate for a similar dashboard with different Supabase records

## Data flow

```
Android App (Room DB) → Sync Service → Supabase (PostgreSQL)
                                              ↓
                              Laravel + Filament Dashboard
                              (reads via materialized views)
```

## Main Supabase tables

| Table | Purpose |
|-------|---------|
| `devices` | Serial numbers, model, MAC, status |
| `frequency_tests` | Frequency test results (pass/fail, timestamps) |
| `song_tests` | Song test results |
| `fqc_records` | Final QC checklist |
| `driver_pairing_records` | Driver pairing data |
| `changed_part_records` | Part swaps |

## What the dashboard should show

- **Device output**: total devices, pass %, fail %, avg time to pass
- **Operator performance**: devices tested, pass rate, rework count, time per device
- **Timeline**: per-device event history
- **Stage breakdown**: Driver Pairing → Frequency → Song Test → FQC

---

# Laravel + Filament: Fundamentals

## 1. Laravel basics (Python analogy)

| Python | Laravel (PHP) |
|--------|---------------|
| `pip install` | `composer require` |
| `python manage.py runserver` | `php artisan serve` |
| Django models | Eloquent models |
| Django admin | Filament admin panel |
| `requirements.txt` | `composer.json` |

## 2. Important Laravel commands

```bash
# Start dev server
php artisan serve

# Clear caches (do this when things look wrong)
php artisan config:clear
php artisan cache:clear
php artisan route:clear
php artisan view:clear
# Or all at once:
php artisan optimize:clear

# Database
php artisan migrate              # Run migrations
php artisan migrate:status       # Check migration status
php artisan tinker               # REPL (like Python shell)

# Filament
php artisan make:filament-user   # Create admin user
php artisan filament:install    # Install Filament
```

## 3. Filament basics

Filament is an admin panel on top of Laravel. It gives you:

- **Pages** – full pages (e.g. dashboards, explorers)
- **Resources** – CRUD for models (like Django admin)
- **Widgets** – cards, charts, stats
- **Tables** – data tables with filters, actions

Typical structure:

```
app/
├── Models/           # Eloquent models (like Django models)
├── Filament/
│   ├── Pages/        # Custom pages (TimelineExplorer, OperatorDashboard)
│   ├── Resources/    # CRUD resources
│   └── Widgets/      # Dashboard widgets (stats, charts)
resources/views/
└── filament/         # Blade templates
```

## 4. How data flows in your project

```
Supabase (PostgreSQL)
    ↓
config/database.php   → defines 'supabase' connection
    ↓
app/Models/*.php      → Eloquent models with $connection = 'supabase'
    ↓
Filament Pages/Widgets → query models, show data
    ↓
Blade templates       → HTML output
```

## 5. Showing information

**A. In a widget (stats card):**

```php
// In a Widget class
protected function getStats(): array
{
    $count = DeviceTestEventsMv::where('event_type', 'frequency_test')->count();
    return [
        Stat::make('Frequency Tests', $count),
    ];
}
```

**B. In a table:**

```php
// In a Filament Page
public static function table(Table $table): Table
{
    return $table
        ->columns([
            TextColumn::make('serial_number'),
            TextColumn::make('event_type'),
            TextColumn::make('event_timestamp')->dateTime(),
        ])
        ->query(DeviceTestEventsMv::query());
}
```

**C. In a Blade view:**

```blade
{{-- resources/views/filament/pages/my-page.blade.php --}}
<div>
    Total devices: {{ $totalDevices }}
</div>
```

## 6. Calculations (like your KPIs)

```php
// Pass percentage
$total = FqcRecord::whereBetween('entry_timestamp', [$start, $end])->count();
$passed = FqcRecord::whereBetween('entry_timestamp', [$start, $end])
    ->where('overall_result', 'PASS')->count();
$passPercent = $total > 0 ? round(($passed / $total) * 100, 1) : 0;

// Average time to pass (conceptual)
$avgTime = DeviceStageSummaryMv::whereBetween('last_update', [$start, $end])
    ->selectRaw('AVG(EXTRACT(EPOCH FROM (last_update - first_test_time))) as avg_seconds')
    ->value('avg_seconds');
```

## 7. Time range filters

Your docs use Today/Week/Month/Year. Typical pattern:

```php
$timeRange = $this->data['timeRange'] ?? 'Month';

$start = match($timeRange) {
    'Today' => now()->startOfDay(),
    'Week'  => now()->startOfWeek(),
    'Month' => now()->startOfMonth(),
    'Year'  => now()->startOfYear(),
    default => now()->subYears(10), // "All"
};

$query->where('event_timestamp', '>=', $start);
```

---

# Common errors and how to fix them

## 1. Column does not exist

```
column "last_update" does not exist
```

- Cause: model or query uses a column that doesn’t exist in the DB/view.
- Fix: Check the actual table/view in Supabase, then update the model and queries to use the correct column (e.g. `event_timestamp` instead of `last_update`).

## 2. Class not found

```
Class "Filament\Tables\Actions\Action" not found
```

- Cause: wrong namespace or Filament version mismatch.
- Fix: Use the correct import, e.g. `\Filament\Actions\Action`, or check Filament docs for your version.

## 3. Database connection failed

```
SQLSTATE[HY000] [2002] Connection refused
```

- Cause: wrong DB host, credentials, or SSL.
- Fix:
  - Use Supabase pooler host (e.g. `aws-1-ap-southeast-2.pooler.supabase.com:5432`)
  - Username: `postgres.[project-ref]`
  - URL-encode special characters in the password
  - Set `DB_SSLMODE=require` for Supabase

## 4. No data showing

- Check Telescope (Logs, Queries, Exceptions).
- Verify time range (e.g. “Today” might filter everything out).
- Clear cache: `php artisan cache:clear`.
- Confirm materialized views are refreshed in Supabase.

## 5. Wrong / stale data

- Materialized views are snapshots; they must be refreshed.
- In Supabase: `REFRESH MATERIALIZED VIEW device_test_events_mv;`
- Or call a refresh function from Laravel (e.g. via a scheduled task).

---

# Debugging workflow

1. **Laravel Telescope** – `/telescope`:
   - Logs
   - Queries
   - Exceptions
   - Requests

2. **Laravel logs** – `storage/logs/laravel.log`

3. **Tinker** – test queries directly:

```bash
php artisan tinker
>>> DB::connection('supabase')->table('device_test_events_mv')->limit(5)->get();
```

4. **Cache** – when things look wrong:

```bash
php artisan optimize:clear
```

---

# Mental model for your project

| Concept | In your project |
|---------|------------------|
| **Models** | `DeviceTestEventsMv`, `FqcRecord`, `FrequencyTest`, etc. |
| **Pages** | Timeline Explorer, Operator Dashboard, Failed Pipeline |
| **Widgets** | FQC Stage Counts, Stage Breakdown Chart, etc. |
| **Data source** | Supabase materialized views + raw tables |
| **Calculations** | Pass %, avg time, rework count, etc. |
| **Filters** | Time range (Today/Week/Month/Year) |

---

# Suggested learning path

1. **Day 1–2**: Laravel basics  
   - Routes, controllers, Blade  
   - Eloquent and DB queries  
   - `.env` and `config/database.php`

2. **Day 3–4**: Filament basics  
   - Create a simple Resource  
   - Create a simple Page and Widget  
   - Use Filament tables and forms

3. **Day 5–6**: Your project specifics  
   - Supabase connection and models  
   - Materialized views and refresh  
   - Recreate one widget from the docs

4. **Day 7+**: Debugging and iteration  
   - Use Telescope and logs  
   - Fix one known bug from the docs  
   - Add one new KPI or filter

---

# Next steps

1. Do you already have the Laravel project (e.g. `rapture-admin`) set up locally?
2. Which part do you want to focus on first:  
   - Laravel/PHP basics  
   - Filament (pages, widgets, tables)  
   - Supabase connection and models  
   - One specific feature (e.g. operator time, device count)?
3. Do you want a small “hello world” Filament page we can build step by step?

Tell me where you are (project setup, PHP experience) and what you want to tackle first, and we can go deeper on that part.
