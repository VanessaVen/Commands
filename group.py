import click


@click.group(chain=True)
@click.option('--common-option1')
@click.option('--common-option2')
@click.pass_context
def main(ctx, common_option1, common_option2):
    ctx.obj = {
        'common_option1': common_option1,
        'common_option2': common_option2,
    }


@main.result_callback()
def process_pipeline(processors, common_option1, common_option2):
    print('common_option1 is', common_option1)
    for func in processors:
        res = func()
        if not res:
            raise click.ClickException('Failed processing!')


@main.command()
@click.option('--cmd1-option', is_flag=True)
def cmd1(cmd1_option):
    def process():
        print('This is cmd1')
        return cmd1_option

    return process


@main.command()
@click.option('--cmd2-option')
def cmd2(cmd2_option):
    def process():
        print('This is cmd2')
        return cmd2_option != 'fail'

    return process


@main.command()
@click.pass_context
def cmd3(ctx):
    def process():
        print('This is cmd3 (common option 1 is: {common_option1}'.format(**ctx.obj))
        return True

    return process


if __name__ == '__main__':
    main()
