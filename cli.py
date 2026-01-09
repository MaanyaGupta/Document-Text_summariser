"""
Document Summarizer - Command Line Interface
"""

import click
import os
import sys

from parsers import detect_and_parse
from summarizers import get_summarizer
from storage import save_summary, get_summary, list_summaries, delete_summary, export_summary


@click.group()
def cli():
    """Document Summarizer CLI - Summarize documents with AI or locally."""
    pass


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--mode', '-m', type=click.Choice(['local', 'online']), default='local',
              help='Summarization mode: local (offline) or online (AI-powered)')
@click.option('--length', '-l', type=click.Choice(['short', 'medium', 'long']), default='medium',
              help='Summary length')
@click.option('--api-key', '-k', envvar='GEMINI_API_KEY',
              help='API key for online mode (or set GEMINI_API_KEY env var)')
@click.option('--save', '-s', is_flag=True, help='Save the summary to database')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def summarize(file_path, mode, length, api_key, save, output):
    """Summarize a document.
    
    Examples:
        python cli.py summarize document.pdf
        python cli.py summarize document.docx --mode online --api-key YOUR_KEY
        python cli.py summarize text.txt --length short --save
    """
    try:
        click.echo(f"📄 Parsing {os.path.basename(file_path)}...")
        text, file_type = detect_and_parse(file_path)
        
        if not text.strip():
            click.echo("❌ No text content found in file", err=True)
            sys.exit(1)
        
        click.echo(f"📊 Document type: {file_type} | Characters: {len(text)}")
        
        if mode == 'online' and not api_key:
            click.echo("❌ API key required for online mode. Use --api-key or set GEMINI_API_KEY", err=True)
            sys.exit(1)
        
        click.echo(f"🔄 Generating {length} summary using {mode} mode...")
        
        summarizer = get_summarizer(mode, api_key)
        summary = summarizer.summarize(text, length)
        key_points = summarizer.extract_key_points(text)
        
        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("📝 SUMMARY")
        click.echo("=" * 60)
        click.echo(summary)
        
        click.echo("\n" + "=" * 60)
        click.echo("📌 KEY POINTS")
        click.echo("=" * 60)
        for i, point in enumerate(key_points, 1):
            click.echo(f"  {i}. {point}")
        
        # Save if requested
        if save:
            summary_id = save_summary(
                filename=os.path.basename(file_path),
                original_text=text,
                summary=summary,
                key_points=key_points,
                mode=mode,
                length=length,
                file_type=file_type
            )
            click.echo(f"\n💾 Saved with ID: {summary_id}")
        
        # Output to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(f"Summary of: {os.path.basename(file_path)}\n")
                f.write("=" * 60 + "\n\n")
                f.write("SUMMARY:\n")
                f.write(summary + "\n\n")
                f.write("KEY POINTS:\n")
                for i, point in enumerate(key_points, 1):
                    f.write(f"{i}. {point}\n")
            click.echo(f"\n📁 Output saved to: {output}")
        
        click.echo("\n✅ Done!")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command('list-saved')
@click.option('--limit', '-n', default=20, help='Number of summaries to show')
def list_saved(limit):
    """List all saved summaries."""
    try:
        summaries = list_summaries(limit)
        
        if not summaries:
            click.echo("📭 No saved summaries found")
            return
        
        click.echo(f"\n📚 Saved Summaries ({len(summaries)} total)\n")
        click.echo("-" * 80)
        
        for s in summaries:
            click.echo(f"ID: {s['id']} | {s['filename']} | {s['mode']}/{s['length']} | {s['created_at']}")
            if s.get('summary_preview'):
                preview = s['summary_preview'][:100] + "..." if len(s.get('summary_preview', '')) > 100 else s.get('summary_preview', '')
                click.echo(f"   └─ {preview}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('summary_id', type=int)
@click.option('--format', '-f', type=click.Choice(['txt', 'json']), default='txt',
              help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export(summary_id, format, output):
    """Export a saved summary.
    
    Examples:
        python cli.py export 1
        python cli.py export 1 --format json --output summary.json
    """
    try:
        content = export_summary(summary_id, format)
        
        if not content:
            click.echo(f"❌ Summary with ID {summary_id} not found", err=True)
            sys.exit(1)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(content)
            click.echo(f"📁 Exported to: {output}")
        else:
            click.echo(content)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('summary_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this summary?')
def delete(summary_id):
    """Delete a saved summary."""
    try:
        if delete_summary(summary_id):
            click.echo(f"🗑️ Summary {summary_id} deleted")
        else:
            click.echo(f"❌ Summary {summary_id} not found", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('summary_id', type=int)
def show(summary_id):
    """Show details of a saved summary."""
    try:
        summary = get_summary(summary_id)
        
        if not summary:
            click.echo(f"❌ Summary {summary_id} not found", err=True)
            sys.exit(1)
        
        click.echo("\n" + "=" * 60)
        click.echo(f"📄 {summary['filename']} (ID: {summary_id})")
        click.echo(f"📅 {summary['created_at']} | Mode: {summary['mode']} | Length: {summary['length']}")
        click.echo("=" * 60)
        
        click.echo("\n📝 SUMMARY:\n")
        click.echo(summary['summary'])
        
        click.echo("\n📌 KEY POINTS:")
        for i, point in enumerate(summary.get('key_points', []), 1):
            click.echo(f"  {i}. {point}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
