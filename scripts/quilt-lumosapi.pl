#!/usr/bin/perl

use English;
use Cwd;
use Getopt::Long;
use File::Basename;
use File::Copy;
use File::stat;
use strict;

my $patches     = "patches/patches";
my $quilt       = `which quilt 2> /dev/null`; chomp($quilt);
my $lndir       = `which lndir 2> /dev/null`; chomp($lndir);
my $rootdir     = getcwd();
my $srcdir      = "$rootdir/src/lumosapi_client";
my $patchdir    = "$rootdir/patches/patches";
my $series      = "";
my $type        = "";
my $builddir    = "";
my $product     = "";

sub usage
{
    print(STDERR "$PROGRAM_NAME\n");
}

sub parse_args
{
    $type     = "";
    $series   = "$rootdir/patches/series/lumosapi-client.series";
    $builddir = "$rootdir/src/lumosapi_client";
    $product  = ".quilt-lumosapi-client";
}

sub sanity_check
{
    my $program;
    my $line;
    my $rc;

    if (!$quilt)
    {
        print(STDERR "Could not find quilt in your path...\n");
        usage();
        exit(-1);
    }

    if (! -e "$rootdir/patches" ||
        ! -e "$rootdir/patches/patches" ||
        ! -e "$rootdir/patches/series" ||
        ! -d "$srcdir")
    {
        print(STDERR "Not running script from proper directory...\n");
        usage();
        exit(-1);
    }

    if(!$series || ! -e $series)
    {
        print(STDERR "Series file not specified...\n");
        usage();
        exit(-1);
    }

    $program = "awk";
    $line = `$program --version > /dev/null 2>&1`;
    $rc = $?; $rc = $rc >> 8;
    if ($rc != 0)
    {
        print(STDERR "Not using GNU $program.  Ensure that GNU $program is first in your path.\n");
        usage();
        exit(-1);
    }

    $program = "diff";
    $line = `$program --version > /dev/null 2>&1`;
    $rc = $?; $rc = $rc >> 8;
    if ($rc != 0)
    {
        print(STDERR "Not using GNU $program.  Ensure that GNU $program is first in your path.\n");
        usage();
        exit(-1);
    }

    $program = "find";
    $line = `$program --version > /dev/null 2>&1`;
    $rc = $?; $rc = $rc >> 8;
    if ($rc != 0)
    {
        print(STDERR "Not using GNU $program.  Ensure that GNU $program is first in your path.\n");
        usage();
        exit(-1);
    }

    $program = "grep";
    $line = `$program --version > /dev/null 2>&1`;
    $rc = $?; $rc = $rc >> 8;
    if ($rc != 0)
    {
        print(STDERR "Not using GNU $program.  Ensure that GNU $program is first in your path.\n");
        usage();
        exit(-1);
    }

    $program = "sed";
    $line = `$program --version > /dev/null 2>&1`;
    $rc = $?; $rc = $rc >> 8;
    if ($rc != 0)
    {
        print(STDERR "Not using GNU $program.  Ensure that GNU $program is first in your path.\n");
        usage();
        exit(-1);
    }
}

sub verify_patches
{
    my @patchset = `quilt series`;
    foreach my $patch (@patchset)
    {
        chomp($patch);
        my $sb = stat($patch);
        if (!$sb)
        {
            print(STDERR "Patch $patch does not exist.\n");
            print(STDERR "Likely someone forgot to push it upstream.\n");
            exit(-1);
        }
        elsif ($sb->size == 0)
        {
            print(STDERR "Patch $patch is empty.\n");
            print(STDERR "Likely someone forgot to push it upstream.\n");
            exit(-1);
        }
    }
}

sub setup_quilt
{
    my $rc = 0;

    printf("Adding patches from: %s\n", basename($series));
    print("--------------------------------------------------\n");
    symlink($series,   "$builddir/series");
    symlink($patchdir, "$builddir/patches");
    chdir($builddir);
    verify_patches();

    $rc = system("$quilt push -a");
    $rc = $rc >> 8;
    if ($rc != 0)
    {
        print(STDERR "FAILED to apply patches.\n");
        exit(-1);
    }
    
    chdir($rootdir);
}

sub customize
{
}

sub complete
{
    system("touch .quilt");
    system("touch $product");
    print("--------------------------------------------------\n");
    printf("Patches from: %s are fully applied\n", basename($series));
    print("--------------------------------------------------\n");
}

######
# Main
######
parse_args();
sanity_check();
setup_quilt();
customize();
complete();
